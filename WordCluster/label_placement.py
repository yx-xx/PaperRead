import numpy as np
from scipy.spatial.distance import pdist, squareform
import plotly.graph_objects as go


def add_cluster_labels(fig, reduced, labels, keywords, dims):
    """为每个点添加标签，使用优化的布局策略"""
    # 计算点的密度
    densities = _calculate_point_density(reduced)
    
    # 选择代表性的点来显示标签
    selected_indices = _select_representative_labels(reduced, densities, labels)
    
    # 为选中的点添加标签
    for idx in selected_indices:
        point = reduced[idx]
        text = keywords[idx]
        # 根据局部密度计算偏移量
        offset = _calculate_dynamic_offset(densities[idx])
        # 计算最佳标签位置
        label_pos = _find_best_label_position(point, reduced, offset, dims)
        fig = _add_label_to_plot(fig, point, text, dims, label_pos)
    
    return fig

def _calculate_point_density(points, sigma=0.1):
    """计算每个点的局部密度"""
    
    # 计算点之间的距离矩阵
    distances = squareform(pdist(points))
    
    # 使用高斯核计算密度
    densities = np.sum(np.exp(-distances**2 / (2*sigma**2)), axis=1)
    
    # 归一化密度值到[0,1]区间
    densities = (densities - np.min(densities)) / (np.max(densities) - np.min(densities))
    
    return densities

def _select_representative_labels(points, densities, labels, max_labels=50):
    """选择代表性的点来显示标签"""
    selected = []
    
    # 确保每个簇至少有一个标签
    for cluster in np.unique(labels):
        cluster_mask = labels == cluster
        cluster_points = points[cluster_mask]
        cluster_densities = densities[cluster_mask]
        
        # 选择密度最低的点（通常在边缘，不容易重叠）
        if len(cluster_points) > 0:
            idx = np.where(cluster_mask)[0][np.argmin(cluster_densities)]
            selected.append(idx)
    
    # 在剩余点中选择密度较低的点
    remaining = set(range(len(points))) - set(selected)
    if remaining:
        remaining = list(remaining)
        remaining_densities = densities[remaining]
        # 选择密度最低的几个点
        n_additional = min(max_labels - len(selected), len(remaining))
        if n_additional > 0:
            additional = np.array(remaining)[np.argsort(remaining_densities)[:n_additional]]
            selected.extend(additional)
    
    return selected

def _calculate_dynamic_offset(density, base_offset=0.1, max_offset=0.3):
    """根据局部密度计算动态偏移量"""
    # 密度越大，偏移量越大
    return base_offset + density * (max_offset - base_offset)

def _find_best_label_position(point, all_points, offset, dims):
    """找到最佳的标签位置"""
    # 尝试8个不同方向的位置
    angles = np.linspace(0, 2*np.pi, 8, endpoint=False)
    best_pos = None
    min_overlap = float('inf')
    
    for angle in angles:
        # 计算候选位置
        if dims == 3:
            dx = offset * np.cos(angle)
            dy = offset * np.sin(angle)
            dz = offset * 0.5  # 在3D中添加垂直偏移
            pos = np.array([point[0] + dx, point[1] + dy, point[2] + dz])
        else:
            dx = offset * np.cos(angle)
            dy = offset * np.sin(angle)
            pos = np.array([point[0] + dx, point[1] + dy])
        
        # 计算与其他点的重叠程度
        distances = np.linalg.norm(all_points - pos, axis=1)
        overlap = np.sum(1 / (1 + distances))
        
        # 更新最佳位置
        if overlap < min_overlap:
            min_overlap = overlap
            best_pos = pos
    
    return best_pos

def _add_label_to_plot(fig, point, text, dims, label_pos):
    """向图表添加带优化位置的标签"""
    if dims == 3:
        # 添加引导线
        fig.add_trace(go.Scatter3d(
            x=[point[0], label_pos[0]],
            y=[point[1], label_pos[1]],
            z=[point[2], label_pos[2]],
            mode='lines',
            line=dict(color='gray', width=1),
            showlegend=False
        ))
        
        # 添加标签
        fig.add_trace(go.Scatter3d(
            x=[label_pos[0]],
            y=[label_pos[1]],
            z=[label_pos[2]],
            mode='text+markers',
            text=[text],
            textposition="top center",
            textfont=dict(size=8),
            marker=dict(size=1, opacity=0),
            showlegend=False
        ))
    else:
        # 添加引导线
        fig.add_trace(go.Scatter(
            x=[point[0], label_pos[0]],
            y=[point[1], label_pos[1]],
            mode='lines',
            line=dict(color='gray', width=1),
            showlegend=False
        ))
        
        # 添加标签
        fig.add_trace(go.Scatter(
            x=[label_pos[0]],
            y=[label_pos[1]],
            mode='text+markers',
            text=[text],
            textposition="top center",
            textfont=dict(size=8),
            marker=dict(size=1, opacity=0),
            showlegend=False
        ))
    
    return fig