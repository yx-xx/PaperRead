import numpy as np
import plotly.graph_objects as go
from typing import List
from config import LABEL_FONT_SIZE, MAX_OFFSET
from scipy.spatial import distance_matrix

# 避免除零错误的小常数
EPSILON = 1e-8

def optimize_label_layout(
    points: np.ndarray,
    labels: List[str],
    dims: int,
    max_iter: int = 100,
    tolerance: float = 1e-4,
    max_offset_ratio: float = MAX_OFFSET
) -> np.ndarray:
    """带最大偏移限制的标签布局优化"""
    # 1. 计算最大允许偏移距离
    min_vals = np.min(points, axis=0)
    max_vals = np.max(points, axis=0)
    data_range = np.max(max_vals - min_vals + EPSILON)
    max_offset_dist = data_range * max_offset_ratio
    
    # 2. 简化标签尺寸估算
    avg_char_width = 7
    avg_height = 15
    label_sizes = np.array([avg_char_width * max(1, len(label)) for label in labels])
    label_sizes = np.column_stack([label_sizes, np.full(len(labels), avg_height)])
    
    # 3. 初始位置：紧贴数据点（改进零向量处理）
    radii = np.linalg.norm(label_sizes, axis=1) * 0.5
    directions = points - np.mean(points, axis=0)
    norms = np.linalg.norm(directions, axis=1)
    
    # 处理零范数情况
    zero_norm_mask = norms < EPSILON
    if np.any(zero_norm_mask):
        # 为这些点生成随机方向
        random_dirs = np.random.randn(np.sum(zero_norm_mask), dims)
        random_dirs /= np.linalg.norm(random_dirs, axis=1)[:, None]
        directions[zero_norm_mask] = random_dirs
        norms[zero_norm_mask] = 1.0
    
    directions = directions / norms[:, np.newaxis]
    positions = points + directions * (radii * 0.1)[:, np.newaxis]
    
    # 4. 带偏移限制的力导向优化
    return optimized_force_layout(
        points, positions, label_sizes, dims, max_iter, tolerance, max_offset_dist
    )

def optimized_force_layout(
    points: np.ndarray,
    positions: np.ndarray,
    label_sizes: np.ndarray,
    dims: int,
    max_iter: int = 100,
    tolerance: float = 1e-4,
    max_offset_dist: float = 0.3
) -> np.ndarray:
    """
    带偏移限制的力导向布局
    """
    # 1. 优化物理参数
    k_repel = 0.05  # 弱排斥
    k_attract = 0.9  # 强吸引
    min_dist = np.mean(np.linalg.norm(label_sizes, axis=1)) * 0.8
    
    # 主优化循环
    for iteration in range(max_iter):
        # 2. 计算排斥力
        repulse = np.zeros_like(positions)
        dists = distance_matrix(positions, positions)
        np.fill_diagonal(dists, np.inf)  # 忽略自身
        
        for i in range(len(positions)):
            close_idx = np.where(dists[i] < min_dist * 2.0)[0]
            
            for j in close_idx:
                if i == j: continue
                
                vec = positions[i] - positions[j]
                dist = np.linalg.norm(vec)
                
                # 处理距离过小的情况
                if dist < EPSILON:
                    # 生成随机方向
                    vec = np.random.randn(dims)
                    dist = np.linalg.norm(vec)
                
                # 应用排斥力
                if dist < min_dist:
                    force = k_repel * (min_dist - dist) / (dist + EPSILON)  # 防止除零
                    repulse[i] += vec * force
        
        # 3. 强吸引力（确保标签靠近原始点）
        attract_vectors = points - positions
        attract_distances = np.linalg.norm(attract_vectors, axis=1)
        
        # 避免除零
        attract_distances[attract_distances < EPSILON] = EPSILON
        normalized_attract = attract_vectors / attract_distances[:, None]
        
        attract = k_attract * normalized_attract * attract_distances[:, None]
        
        # 4. 组合位移
        displacement = repulse + attract
        
        # 5. 应用位移（带自适应缩放）
        step_factor = min(0.8, 0.2 + iteration * 0.02)
        positions += displacement * step_factor
        
        # 6. 强制偏移限制 (修复除零错误)
        offsets = np.linalg.norm(positions - points, axis=1)
        over_offset = offsets > max_offset_dist
        
        if np.any(over_offset):
            # 创建向量指向原始点
            pull_back_vectors = points[over_offset] - positions[over_offset]
            pull_back_distances = np.linalg.norm(pull_back_vectors, axis=1)
            
            # 处理零距离情况
            zero_idx = pull_back_distances < EPSILON
            if np.any(zero_idx):
                # 为距离接近零的点生成随机方向
                random_dirs = np.random.randn(np.sum(zero_idx), dims)
                random_dirs /= np.linalg.norm(random_dirs, axis=1)[:, None]
                pull_back_vectors[zero_idx] = random_dirs * max_offset_dist
                pull_back_distances[zero_idx] = max_offset_dist
            
            # 计算单位方向向量
            pull_back_dirs = pull_back_vectors / pull_back_distances[:, None]
            
            # 设置到最大偏移位置
            positions[over_offset] = points[over_offset] + pull_back_dirs * max_offset_dist
        
        # 7. 收敛检测
        max_move = np.max(np.linalg.norm(displacement, axis=1))
        if max_move < tolerance:
            break
    
    return positions

def add_cluster_labels(
    fig: go.Figure,
    reduced: np.ndarray,
    labels: List[str],
    keywords: List[str],
    dims: int
) -> go.Figure:
    """
    添加集群标签的实现（带最大偏移控制）
    """
    # 使用20%的数据范围作为最大偏移
    positions = optimize_label_layout(reduced, keywords, dims, max_offset_ratio=MAX_OFFSET)
    
    # 计算实际平均偏移（安全计算）
    offsets = np.linalg.norm(positions - reduced, axis=1)
    avg_offset = np.mean(offsets)
    
    # 计算最大允许偏移
    min_vals = np.min(reduced, axis=0)
    max_vals = np.max(reduced, axis=0)
    data_range = np.max(max_vals - min_vals)
    max_offset_allowed = data_range * 0.2
    
    print(f"平均标签偏移: {avg_offset:.4f} (最大允许: {max_offset_allowed:.4f})")
    
    for point, text, pos in zip(reduced, keywords, positions):
        # 检查是否是可数的位置（非NaN）
        if np.any(np.isnan(pos)):
            # 使用原始点位置作为备选
            pos = point.copy()
            print(f"警告: 标签 '{text}' 位置无效，使用原始位置")
            
        # 添加连接线
        if dims == 3:
            fig.add_trace(go.Scatter3d(
                x=[point[0], pos[0]],
                y=[point[1], pos[1]],
                z=[point[2], pos[2]],
                mode='lines',
                line=dict(width=1, color='rgba(100,100,100,0.5)'),
                showlegend=False
            ))
            fig.add_trace(go.Scatter3d(
                x=[pos[0]], y=[pos[1]], z=[pos[2]],
                mode='text',
                text=text,
                textposition="middle center",
                textfont=dict(size=LABEL_FONT_SIZE),
                showlegend=False
            ))
        else:
            fig.add_trace(go.Scatter(
                x=[point[0], pos[0]],
                y=[point[1], pos[1]],
                mode='lines',
                line=dict(width=1, color='rgba(100,100,100,0.5)'),
                showlegend=False
            ))
            fig.add_trace(go.Scatter(
                x=[pos[0]], y=[pos[1]],
                mode='text',
                text=text,
                textposition="middle center",
                textfont=dict(size=LABEL_FONT_SIZE),
                showlegend=False
            ))
    
    return fig