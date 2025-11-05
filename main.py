import streamlit as st
import json
import plotly.graph_objects as go
from Algorithms.a_star import a_star_search
from Algorithms.dijkstras import dijkstra
from Algorithms.heuristics import euclidean_distance, manhattan_distance

st.set_page_config(
    page_title="Smart Campus Navigation",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_campus_data():
    with open('Data/campus_map.json', 'r') as file:
        data = json.load(file)
    return data

def create_map_visualization(graph, path=None, explored_nodes=None):
    nodes = graph['nodes']
    edges = graph['edges']
    blocked_paths = graph.get('blocked_paths', [])
    fig = go.Figure()

    for edge in edges:
        from_node = nodes[edge['from']]
        to_node = nodes[edge['to']]
        is_in_path = False
        if path and len(path) > 1:
            for i in range(len(path) - 1):
                if (path[i] == edge['from'] and path[i+1] == edge['to']) or \
                   (path[i] == edge['to'] and path[i+1] == edge['from']):
                    is_in_path = True
                    break
        edge_id = f"{edge['from']}-{edge['to']}"
        is_blocked = edge_id in blocked_paths
        if is_blocked:
            color = 'red'
            width = 2
        elif is_in_path:
            color = 'green'
            width = 5
        else:
            color = 'lightgray'
            width = 2
        fig.add_trace(go.Scatter(
            x=[from_node['x'], to_node['x']],
            y=[from_node['y'], to_node['y']],
            mode='lines',
            line=dict(color=color, width=width),
            hovertemplate=f"<b>{edge['from']} → {edge['to']}</b><br>" +
                          f"Distance: {edge.get('distance','?')}m<br>" +
                          f"Type: {edge.get('type','')}" + "<extra></extra>",
            showlegend=False
        ))

    node_x, node_y, node_text, node_colors, node_sizes = [], [], [], [], []
    for node_id, node_data in nodes.items():
        node_x.append(node_data['x'])
        node_y.append(node_data['y'])
        node_text.append(node_data.get('name', node_id))
        if path and node_id == path[0]:
            node_colors.append('blue')
            node_sizes.append(25)
        elif path and node_id == path[-1]:
            node_colors.append('red')
            node_sizes.append(25)
        elif path and node_id in path:
            node_colors.append('green')
            node_sizes.append(18)
        elif explored_nodes and node_id in explored_nodes:
            node_colors.append('orange')
            node_sizes.append(15)
        else:
            node_colors.append('lightblue')
            node_sizes.append(15)

    fig.add_trace(go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        marker=dict(
            size=node_sizes,
            color=node_colors,
            line=dict(width=2, color='black')
        ),
        text=node_text,
        textposition='top center',
        textfont=dict(size=10, color='black'),
        hovertemplate='<b>%{text}</b><extra></extra>',
        showlegend=False
    ))

    fig.update_layout(
        title={
            'text': "Campus Navigation Map",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#2c3e50'}
        },
        showlegend=False,
        hovermode='closest',
        plot_bgcolor='#f8f9fa',
        paper_bgcolor='white',
        xaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            zeroline=False,
            showticklabels=False,
            title=""
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            zeroline=False,
            showticklabels=False,
            title=""
        ),
        height=600,
        margin=dict(l=20, r=20, t=60, b=20)
    )

    return fig

def main():
    st.title("🗺️ Smart Campus Navigation System")
    st.markdown("**Find the optimal path between any two campus locations using AI algorithms**")
    st.markdown("---")

    graph = load_campus_data()
    nodes = graph['nodes']
    if isinstance(nodes, list):
        nodes = {node['name']: node for node in nodes}
    graph['nodes'] = nodes
    node_names = list(nodes.keys())

    st.sidebar.header("⚙️ Navigation Settings")
    st.sidebar.subheader("📍 Select Locations")

    start_name = st.sidebar.selectbox("Starting Point:", options=node_names, index=0)
    start = start_name
    default_goal_index = 3 if len(node_names) > 3 else max(0, len(node_names) - 1)
    goal_name = st.sidebar.selectbox("Destination:", options=node_names, index=default_goal_index)
    goal = goal_name

    st.sidebar.markdown("---")
    st.sidebar.subheader("🧠 Select Algorithm")

    algorithm = st.sidebar.radio(
        "Choose pathfinding algorithm:",
        options=["A* (Euclidean Heuristic)", "A* (Manhattan Heuristic)", "Dijkstra's Algorithm"],
        index=0
    )

    st.sidebar.markdown("---")
    find_button = st.sidebar.button("🔍 Find Path", type="primary", use_container_width=True)

    if find_button:
        if start == goal:
            st.error("❌ Start and destination cannot be the same!")
            return
        with st.spinner("🔄 Finding optimal path..."):
            if "Euclidean" in algorithm:
                result = a_star_search(graph, start, goal, euclidean_distance)
            elif "Manhattan" in algorithm:
                result = a_star_search(graph, start, goal, manhattan_distance)
            else:
                result = dijkstra(graph, start, goal)
            st.session_state['result'] = result
            st.session_state['algorithm'] = algorithm

    if 'result' in st.session_state:
        result = st.session_state['result']
        algo_name = st.session_state['algorithm']
        if result['success']:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.subheader("🗺️ Campus Map")
                fig = create_map_visualization(graph, path=result['path'], explored_nodes=result.get('all_explored', []))
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                st.subheader("📊 Navigation Results")
                st.success("✅ Path Found!")
                st.metric("Algorithm Used", algo_name)
                st.metric("Total Distance", f"{result['cost']:.1f} meters")
                st.metric("Nodes Explored", result.get('nodes_explored', 0))
                st.metric("Path Length", f"{len(result['path'])} locations")
                walking_speed = 1.4
                time_seconds = result['cost'] / walking_speed
                time_minutes = time_seconds / 60
                st.metric("Estimated Time", f"{time_minutes:.1f} minutes")
                st.markdown("---")
                st.markdown("### 🛤️ Step-by-Step Route")
                for i, node_id in enumerate(result['path'], 1):
                    if i == 1:
                        icon = "📍"
                    elif i == len(result['path']):
                        icon = "🎯"
                    else:
                        icon = "➜"
                    st.write(f"{icon} **Step {i}:** {nodes[node_id]['name']}")
        else:
            st.error("❌ No path found between selected locations!")
            fig = create_map_visualization(graph)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("👆 Select start and destination from the sidebar, then click on 'Find Path'")
        fig = create_map_visualization(graph)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: gray; padding: 20px;'>
            <p><b>🎓 Smart Campus Navigation System</b></p>
            <p>Minor Project - Artificial Intelligence | Built with Python, Streamlit & Plotly</p>
            <p>Made By AAYUSH KUMAR</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
