import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import numpy as np
from config import REDUCE_METHOD, LABEL_DENSITY, PLOT_SIZE, PLOT_FILE, DIMSIONS, INTERACTIVE
from config import MARKER_DEFAULT_SIZE, DEFAULT_OPACITY, MARKER_HIGHLIGHT_SIZE, HIGHLIGHT_OPACITY
import matplotlib.font_manager as fm
import os
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def visualize_clusters(X, labels, keywords, interactive_=INTERACTIVE, dims_=DIMSIONS):
    """
    聚类可视化的统一入口函数
    
    参数:
        X: 降维前的特征矩阵
        labels: 聚类标签
        keywords: 关键词列表
        interactive_: 是否使用交互式可视化
        dims: 维度 (2 或 3)
    """
    if interactive_:
        return visualize_clusters_interactive(X, labels, keywords, dims_)
    else:
        return visualize_clusters_static(X, labels, keywords)




#################################### visualize_clusters_interactive ##################################

def visualize_clusters_interactive(X, labels, keywords, dims_):
    """交互式聚类可视化（基于Plotly）"""
    # 参数检查
    if dims_ not in [2, 3]:
        raise ValueError("维度必须是2或3")
    
    # 降维处理
    reduced, method_name = _reduce_dimensions(X, dims_)
    
    # 数据准备
    df = _prepare_visualization_data(reduced, labels, keywords)
    
    # 创建基础图表
    fig = _create_base_plot(df, dims_, method_name)
    
    # 添加标签
    fig = _add_cluster_labels(fig, reduced, labels, keywords, dims_)
    
    # 保存和显示
    _save_and_show_plot(fig)
    
    return fig


def _reduce_dimensions(X, method_=REDUCE_METHOD, dims_=DIMSIONS):
    """降维处理，支持2D和3D"""
    if method_ == "tsne":
        reducer = TSNE(n_components=dims_, random_state=42)
        reduced = reducer.fit_transform(X.toarray() if hasattr(X, 'toarray') else X)
        method_name = "t-SNE"
    else:
        reducer = PCA(n_components=dims_, random_state=42)
        reduced = reducer.fit_transform(X.toarray() if hasattr(X, 'toarray') else X)
        method_name = "PCA"
    return reduced, method_name



def _prepare_visualization_data(reduced, labels, keywords):
    """准备可视化数据"""
    dims = reduced.shape[1]
    df = pd.DataFrame(reduced, columns=[f'Dimension {i+1}' for i in range(dims)])
    df['Cluster'] = labels
    df['Keyword'] = keywords
    return df


def _create_base_plot(df, dims, method_name):
    """创建基础图表"""
    total_points = len(df)
    
    # 创建基础图表
    if dims == 3:
        fig = px.scatter_3d(
            df, 
            x='Dimension 1', y='Dimension 2', z='Dimension 3',
            color='Cluster',
            # 鼠标悬停时显示关键词文本
            hover_data=['Keyword'],
            title=f'关键词聚类可视化 ({method_name} 3D) - 共{total_points}个关键词',
            labels={'Cluster': '聚类簇'},
            template='plotly_dark'
        )
    else:
        fig = px.scatter(
            df,
            x='Dimension 1', y='Dimension 2',
            color='Cluster',
            hover_data=['Keyword'],
            title=f'关键词聚类可视化 ({method_name} 2D) - 共{total_points}个关键词',
            labels={'Cluster': '聚类簇'},
            template='plotly_dark'
        )
    
    # 准备左侧关键词列表
    cluster_info = {}
    for cluster, keyword in zip(df['Cluster'], df['Keyword']):
        if cluster not in cluster_info:
            cluster_info[cluster] = []
        cluster_info[cluster].append(keyword)
    
    # 创建左侧按钮组
    buttons = []

    # 添加重置按钮
    reset_button = dict(
        args=[{
            'marker.size': [MARKER_DEFAULT_SIZE]*len(df),  # 所有点恢复默认大小
            'marker.opacity': [DEFAULT_OPACITY]*len(df)  # 所有点恢复默认透明度
        }],
        label='重置视图',
        method='restyle'
    )
    buttons.append(reset_button)

    # 遍历每个簇，添加下拉菜单按钮
    # 高亮显示选中关键词
    for cluster in sorted(cluster_info.keys()):
        keywords = cluster_info[cluster]
        for keyword in keywords:
            buttons.append(dict(
                args=[{
                    'marker.size': [MARKER_HIGHLIGHT_SIZE if k == keyword else MARKER_DEFAULT_SIZE for k in df['Keyword']],
                    'marker.opacity': [HIGHLIGHT_OPACITY if k == keyword else DEFAULT_OPACITY for k in df['Keyword']]
                }],
                label=f'簇{cluster}: {keyword}',
                method='restyle'
            ))
    
    # 更新布局，添加左侧面板和控件
    fig.update_layout(
        updatemenus=[
            dict(
                buttons=buttons,
                direction="down",
                showactive=True,
                x=-0.4,
                xanchor="left",
                y=1,
                yanchor="top",
                bgcolor="rgba(255, 255, 255, 0.9)",
                font=dict(size=10, color="black"),
                # 为下拉菜单添加边框增强视觉
                bordercolor="rgba(150, 150, 150, 0.3)",
                borderwidth=1
            )
        ],
        margin=dict(l=175, r=20, t=100, b=20),  # 增大顶部边距容纳提示信息
    )
    
    return fig

def _add_cluster_labels(fig, reduced, labels, keywords, dims):
    """为每个点添加标签"""
    for i, (point, keyword) in enumerate(zip(reduced, keywords)):
        fig = _add_label_to_plot(fig, point, keyword, dims)
    return fig

def _add_label_to_plot(fig, point, text, dims):
    """向图表添加带引导线的标签"""
    offset = 0.1  # 标签偏移量
    
    if dims == 3:
        # 添加引导线
        fig.add_trace(go.Scatter3d(
            x=[point[0], point[0]+offset],
            y=[point[1], point[1]+offset],
            z=[point[2], point[2]+offset],
            mode='lines',
            line=dict(color='gray', width=1),
            showlegend=False
        ))
        
        # 添加标签
        fig.add_trace(go.Scatter3d(
            x=[point[0]+offset],
            y=[point[1]+offset],
            z=[point[2]+offset],
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
            x=[point[0], point[0]+offset],
            y=[point[1], point[1]+offset],
            mode='lines',
            line=dict(color='gray', width=1),
            showlegend=False
        ))
        
        # 添加标签
        fig.add_trace(go.Scatter(
            x=[point[0]+offset],
            y=[point[1]+offset],
            mode='text+markers',
            text=[text],
            textposition="top center",
            textfont=dict(size=8),
            marker=dict(size=1, opacity=0),
            showlegend=False
        ))
    
    return fig


# 暂时弃用
def _select_representative_points(points, keywords, centroid, n_labels=None):
    """选择簇中的代表性点"""
    if n_labels is None:
        n_labels = max(1, int(len(points) * LABEL_DENSITY))
    
    dists = np.linalg.norm(points - centroid, axis=1)
    closest_indices = np.argsort(dists)[:n_labels]
    
    return points[closest_indices], keywords[closest_indices]


# def _add_label_to_plot(fig, point, text, dims):
#     """向图表添加单个标签"""
#     if dims == 3:
#         fig.add_trace(go.Scatter3d(
#             x=[point[0]], y=[point[1]], z=[point[2]],
#             mode='text',
#             text=[text],
#             textposition="top center",
#             showlegend=False
#         ))
#     else:
#         fig.add_trace(go.Scatter(
#             x=[point[0]], y=[point[1]],
#             mode='text',
#             text=[text],
#             textposition="top center",
#             showlegend=False
#         ))
#     return fig


def _save_and_show_plot(fig):
    """保存并显示图表"""
    fig.write_html(PLOT_FILE.replace('.png', '.html'))
    fig.show()




#################################### visualize_clusters_static ##################################

# matplotlib找不到字体就很头疼，被迫添加丑陋函数
def get_system_chinese_font():
    """获取系统中文字体（优化版）"""
    try:
        # 首选方法：使用Matplotlib的语言选择
        return fm.FontProperties(family='sans-serif', language='zh')
    except Exception as e:
        print(f"警告：无法获取系统中文默认字体 ({e})")
    
    # 备选方法：尝试已知字体路径
    fallback_paths = [
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/arphic-uming/uming.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"
    ]
    
    for path in fallback_paths:
        if os.path.exists(path):
            return fm.FontProperties(fname=path)
    
    # 最终回退
    print("警告：未找到合适的中文字体，使用默认字体")
    return fm.FontProperties()


def visualize_clusters_static(X, labels, keywords):
    """聚类结果可视化 - 安全版本（不影响系统字体设置）"""
    # 获取系统自带的中文字体（不下载新字体）
    chinese_font = get_system_chinese_font()
    
    # 降维处理
    if REDUCE_METHOD == "tsne":
        reducer = TSNE(n_components=2, random_state=42)
        reduced = reducer.fit_transform(X.toarray() if hasattr(X, 'toarray') else X)
        method_name = "t-SNE"
    else:
        reducer = PCA(n_components=2, random_state=42)
        reduced = reducer.fit_transform(X.toarray() if hasattr(X, 'toarray') else X)
        method_name = "PCA"
    
    # 创建可视化
    plt.figure(figsize=PLOT_SIZE)
    scatter = plt.scatter(
        reduced[:, 0], reduced[:, 1],
        c=labels, cmap='viridis', 
        alpha=0.6, edgecolors='w', 
        s=60
    )
    
    # 标注策略：簇中心点 + 随机样本
    label_points = []
    label_texts = []
    
    # 1. 标注每个簇的中心点
    for cluster_id in np.unique(labels):
        cluster_mask = (labels == cluster_id)
        cluster_points = reduced[cluster_mask]
        
        if len(cluster_points) > 0:
            centroid = np.mean(cluster_points, axis=0)
            dists = np.linalg.norm(cluster_points - centroid, axis=1)
            centroid_idx = np.argmin(dists)
            
            # 获取原始数据中的全局索引
            global_idx = np.where(cluster_mask)[0][centroid_idx]
            label_points.append(reduced[global_idx])
            label_texts.append(keywords[global_idx])
    
    # 2. 添加额外随机标签
    n_additional = int(LABEL_DENSITY * len(keywords))
    additional_indices = np.random.choice(len(keywords), n_additional, replace=False)
    
    for idx in additional_indices:
        label_points.append(reduced[idx])
        label_texts.append(keywords[idx])
    
    # 创建标注对象（避免重复）
    unique_texts = {}
    points_to_plot = []
    texts_to_plot = []
    for point, text in zip(label_points, label_texts):
        if text not in unique_texts:
            unique_texts[text] = True
            points_to_plot.append(point)
            texts_to_plot.append(text)
    
    # 添加标注 - 仅在此处应用字体（不影响系统）
    for point, text in zip(points_to_plot, texts_to_plot):
        plt.annotate(
            text, 
            point, 
            fontsize=9, 
            alpha=0.8,
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.7),
            fontproperties=chinese_font  # 应用选择的字体
        )
    
    # 标题 - 也应用选择的字体
    title = f'关键词聚类可视化 ({method_name}降维)'
    plt.title(title, fontproperties=chinese_font)
    
    plt.colorbar(scatter, label='聚类簇')
    plt.xticks([])
    plt.yticks([])
    plt.grid(alpha=0.1)
    
    # 保存结果（不会修改系统设置）
    plt.savefig(PLOT_FILE, dpi=300, bbox_inches='tight')
    print(f"可视化结果已保存至: {PLOT_FILE}")
    plt.show()

