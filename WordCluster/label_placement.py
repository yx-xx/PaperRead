import numpy as np
from scipy.spatial import cKDTree
import plotly.graph_objects as go
import warnings
from typing import List
from scipy.spatial.distance import pdist, squareform
from config import LABEL_FONT_SIZE


def optimize_label_layout(
    points: np.ndarray,
    labels: List[str],
    dims: int,
    max_iter: int = 100,
    tolerance: float = 1e-4,
    max_labels: int = 1000
)-> np.ndarray:
    """
    优化标签布局，防止重叠并保证可读性
    
    参数:
    points - 点坐标数组 (N, dims)
    labels - 标签文本列表
    dims - 维度 (2或3)
    max_iter - 最大迭代次数
    tolerance - 收敛容忍度
    max_labels - 最大标签数量限制
    
    返回:
    np.ndarray - 优化后的标签位置数组 (N, dims)
    """
    if len(points) > max_labels:
        warnings.warn(f"点数量({len(points)})超过安全阈值({max_labels})，进行下采样", RuntimeWarning)
        indices = np.random.choice(len(points), max_labels, replace=False)
        points = points[indices]
        labels = [labels[i] for i in indices]
    
    # 估计标签尺寸
    label_sizes = np.array([estimate_label_size(label, dims) for label in labels])
    
    # 初始位置（沿径向偏移）
    initial_positions = initial_radial_offset(points, label_sizes, dims)
    
    # 约束力导向优化
    positions = force_directed_layout(
        points, initial_positions, label_sizes, dims, max_iter, tolerance
    )
    
    # 重叠消除
    positions = eliminate_overlaps(points, positions, label_sizes, dims)
    
    return positions

def estimate_label_size(label: str, dims: int)-> np.ndarray:
    """根据标签文本估算尺寸（简化版）"""
    # 实际应用中可用更复杂的度量方法
    text_length = len(label)
    font_height = 8  # 像素高度
    font_width = 4  # 每个字符的近似宽度
    
    width = max(20, text_length * font_width * 0.7)  # 标签宽度
    height = max(10, font_height * 1.2)  # 标签高度
    
    # 在三维中，增加"深度"维度
    if dims == 3:
        return np.array([width, height, 0.5 * height])
    return np.array([width, height])

def initial_radial_offset(
    points: np.ndarray, 
    label_sizes: np.ndarray,
    dims: int
) -> np.ndarray:
    """计算初始径向偏移位置"""
    # 计算点密度
    densities = calculate_point_density(points)
    
    # 计算基础偏移量
    base_offsets = np.linalg.norm(label_sizes, axis=1) * 0.5
    
    positions = []
    for i, point in enumerate(points):
        # 随机角度
        angle = np.random.rand() * 2 * np.pi
        
        # 三维需要第二个角度
        angle_z = np.random.rand() * np.pi if dims == 3 else 0
        
        # 动态偏移量
        offset = base_offsets[i] + densities[i] * base_offsets[i]
        
        # 计算位置
        if dims == 3:
            dx = offset * np.cos(angle) * np.sin(angle_z)
            dy = offset * np.sin(angle) * np.sin(angle_z)
            dz = offset * np.cos(angle_z)
            positions.append(point + np.array([dx, dy, dz]))
        else:
            dx = offset * np.cos(angle)
            dy = offset * np.sin(angle)
            positions.append(point + np.array([dx, dy]))
    
    return np.array(positions)

def calculate_point_density(points: np.ndarray, sigma: float = 0.1) -> np.ndarray:
    """计算点密度（高斯核密度估计）"""
    distances = squareform(pdist(points))
    densities = np.sum(np.exp(-distances**2 / (2*sigma**2)), axis=1)
    return (densities - np.min(densities)) / (np.max(densities) - np.min(densities) + 1e-8)

def force_directed_layout(
    points: np.ndarray,
    label_positions: np.ndarray,
    label_sizes: np.ndarray,
    dims: int,
    max_iter: int = 100,
    tolerance: float = 1e-4
) -> np.ndarray:
    """
    力导向标签布局优化
    """
    # 物理参数
    k_repel = 0.8  # 排斥力系数
    k_attract = 0.05  # 吸引力系数
    max_displacement = 0.5  # 最大位移限制
    
    # 加速结构
    tree = cKDTree(label_positions)
    
    for iteration in range(max_iter):
        displacement = np.zeros_like(label_positions)
        
        # 计算排斥力
        for i in range(len(label_positions)):
            # 找到附近的标签
            max_dist = np.linalg.norm(label_sizes[i]) * 1.5
            neighbors = tree.query_ball_point(label_positions[i], max_dist)
            
            for j in neighbors:
                if j <= i:
                    continue
                    
                # 计算重叠排斥力
                direction = label_positions[i] - label_positions[j]
                distance = np.linalg.norm(direction)
                
                if distance < 1e-6:
                    direction = np.random.randn(dims)
                    distance = np.linalg.norm(direction)
                
                min_distance = (np.linalg.norm(label_sizes[i]) + 
                                np.linalg.norm(label_sizes[j])) * 0.5
                
                if distance < min_distance:
                    force = k_repel * (min_distance - distance) / distance
                    displacement[i] += direction * force
                    displacement[j] -= direction * force
        
        # 计算吸引力（保持标签靠近原始点）
        attract_vectors = points - label_positions
        attract_distances = np.linalg.norm(attract_vectors, axis=1)
        
        for i in range(len(attract_vectors)):
            if attract_distances[i] > 1e-6:
                normalized = attract_vectors[i] / attract_distances[i]
                displacement[i] += k_attract * attract_distances[i] * normalized
        
        # 应用位移（限制最大位移）
        displacement_norms = np.linalg.norm(displacement, axis=1)
        scale_factors = np.minimum(max_displacement / displacement_norms, 1)
        displacement *= scale_factors[:, np.newaxis]
        
        # 更新位置
        new_positions = label_positions + displacement
        
        # 检查收敛
        max_displacement = np.max(scale_factors * displacement_norms)
        if max_displacement < tolerance:
            break
        
        # 更新加速结构
        tree = cKDTree(new_positions)
        label_positions = new_positions
    
    return label_positions

def eliminate_overlaps(
    points: np.ndarray,
    label_positions: np.ndarray,
    label_sizes: np.ndarray,
    dims: int
) -> np.ndarray:
    """
    贪婪重叠消除 - 使用优先级队列逐步移除重叠
    """
    # 创建优先级队列（按密度排序，密度大的优先）
    densities = calculate_point_density(points)
    priority = np.argsort(-densities)  # 降序
    
    # 创建已放置标签列表
    placed_labels = []
    
    # 创建加速结构
    tree = cKDTree(label_positions)
    
    # 处理每个标签
    for i in priority:
        original_position = label_positions[i]
        current_position = original_position
        size = np.linalg.norm(label_sizes[i])
        overlap = True
        attempts = 0
        max_attempts = 20
        
        # 尝试微调位置消除重叠
        while overlap and attempts < max_attempts:
            overlap = False
            
            # 检查与已放置标签的重叠
            neighbors = tree.query_ball_point(current_position, size * 1.5)
            
            for j in neighbors:
                if j == i or j not in placed_labels:
                    continue
                    
                distance = np.linalg.norm(current_position - label_positions[j])
                min_distance = (size + np.linalg.norm(label_sizes[j])) * 0.5
                
                if distance < min_distance:
                    overlap = True
                    # 计算微调方向
                    direction = current_position - label_positions[j]
                    if np.linalg.norm(direction) < 1e-6:
                        direction = np.random.randn(dims)
                    direction = direction / np.linalg.norm(direction)
                    
                    # 应用微调
                    displacement = (min_distance - distance) * 0.5 * direction
                    current_position += displacement
                    attempts += 1
                    break
        
        # 更新位置
        label_positions[i] = current_position
        
        # 更新加速结构
        placed_labels.append(i)
        tree = cKDTree(label_positions[placed_labels])
    
    return label_positions

def add_cluster_labels(
    fig: go.Figure,
    reduced: np.ndarray,
    labels: List[str],
    keywords: List[str],
    dims: int
) -> go.Figure:
    """
    添加优化后的集群标签
    
    参数:
    fig - Plotly图表对象
    reduced - 降维后的坐标数组
    labels - 聚类标签数组
    keywords - 关键词列表
    dims - 维度 (2 或 3)
    """
    # 优化标签位置
    label_positions = optimize_label_layout(reduced, keywords, dims)
    
    # 添加标签
    for i, (point, text, label_pos) in enumerate(zip(reduced, keywords, label_positions)):
        fig = _add_label_to_plot(fig, point, text, dims, label_pos)
    
    return fig

def _add_label_to_plot(
    fig: go.Figure, 
    point: np.ndarray, 
    text: str, 
    dims: int, 
    label_pos: np.ndarray
) -> go.Figure:
    """添加标签到图表，使用更美观的视觉样式"""
    # 计算字体大小（根据文本长度）
    # text_length = len(text)
    font_size = LABEL_FONT_SIZE
    
    # 添加连接线
    line_kwargs = {
        'mode': 'lines',
        'line': dict(color='rgba(150, 150, 150, 0.7)', width=1),
        'showlegend': False,
        'hoverinfo': 'none'
    }
    
    if dims == 3:
        fig.add_trace(go.Scatter3d(
            x=[point[0], label_pos[0]],
            y=[point[1], label_pos[1]],
            z=[point[2], label_pos[2]],
            **line_kwargs
        ))
        
        # 添加标签
        fig.add_trace(go.Scatter3d(
            x=[label_pos[0]],
            y=[label_pos[1]],
            z=[label_pos[2]],
            mode='text',
            text=[text],
            textposition="middle center",
            textfont=dict(size=font_size),
            showlegend=False,
            hoverinfo='text'
        ))
    else:
        fig.add_trace(go.Scatter(
            x=[point[0], label_pos[0]],
            y=[point[1], label_pos[1]],
            **line_kwargs
        ))
        
        # 添加标签
        fig.add_trace(go.Scatter(
            x=[label_pos[0]],
            y=[label_pos[1]],
            mode='text',
            text=[text],
            textposition="middle center",
            textfont=dict(size=font_size),
            showlegend=False,
            hoverinfo='text'
        ))
    
    return fig