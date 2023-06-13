import os
import requests
from flask import Flask, render_template, request
from main import conn, get_subscribers_info, get_amount_of_posts, get_group_photo
from bokeh.embed import components
from bokeh.palettes import Spectral4
from bokeh.plotting import from_networkx
import networkx as nx
from bokeh.models import (BoxSelectTool, Circle, Column, EdgesAndLinkedNodes,
                          HoverTool, MultiLine, NodesAndAdjacentNodes,
                          NodesAndLinkedEdges, Plot, Range1d, Row, TapTool, BoxZoomTool, ResetTool)
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def main_sait():
    with open(os.path.join('C:\Flask Project\static\id_vk', 'vk.txt'), 'r') as group:
        group_id = group.read()
    if request.method == 'POST':
        group_id = request.form.get('id')
        filepath_url = 'C:\Flask Project\static\id_vk'
        filename_url = 'vk.txt'
        f = open(os.path.join(filepath_url, filename_url), 'w')
        f.write(group_id)
        return render_template('index.html', id=group_id)
    else:

        return render_template('index.html', id=group_id)


@app.route('/analitic')
def analitic():
    cur = conn.cursor()
    cur.execute('select post_url, amount_of_likes from top_10_posts_by_group;')
    top_10 = cur.fetchall()
    cur.close()
    count_posts = get_amount_of_posts()
    group = get_group_photo()

    filepath_img = 'C:\Flask Project\static\images'
    url = group[0]
    filename_img = 'avatar.jpg'
    response = requests.get(url)

    if response.status_code == 200:
        with open(os.path.join(filepath_img, filename_img, ), 'wb') as imgfile:
            imgfile.write(response.content)

    return render_template('analitic.html', count_posts=count_posts, group=group,top_10=top_10,)


@app.route('/users')
def users():
    cur = conn.cursor()
    cur.execute('select count(user_id), vk_group_url from user_vk_group group by vk_group_url order by count desc limit 10;')
    top_10 = cur.fetchall()
    cur.execute('select count(topic_group), topic_group from vk_group_id_topic group by topic_group order by count desc limit 10;')
    group_theme = cur.fetchall()
    cur.close()

    users_count = get_subscribers_info()
    return render_template('users.html', users_count=users_count, top_10_group=top_10, groups=group_theme )


@app.route('/interest')
def interest():
    G = nx.karate_club_graph()

    SAME_CLUB_COLOR, DIFFERENT_CLUB_COLOR = "black", "red"
    edge_attrs = {}

    for start_node, end_node, _ in G.edges(data=True):
        edge_color = SAME_CLUB_COLOR if G.nodes[start_node]["club"] == G.nodes[end_node][
            "club"] else DIFFERENT_CLUB_COLOR
        edge_attrs[(start_node, end_node)] = edge_color

    nx.set_edge_attributes(G, edge_attrs, "edge_color")

    # Show with Bokeh
    plot = Plot(width=800, height=800,
                x_range=Range1d(-1.1, 1.1), y_range=Range1d(-1.1, 1.1))
    plot.title.text = "Граф"

    node_hover_tool = HoverTool(tooltips=[("index", "@index"), ("club", "@club")])
    plot.add_tools(node_hover_tool, BoxZoomTool(), ResetTool())

    graph_renderer = from_networkx(G, nx.spring_layout, scale=1, center=(0, 0))

    graph_renderer.node_renderer.glyph = Circle(size=15, fill_color=Spectral4[0])
    graph_renderer.edge_renderer.glyph = MultiLine(line_color="edge_color", line_alpha=0.8, line_width=1)
    plot.renderers.append(graph_renderer)

    script, div = components(plot)

    zxc = []
    qwer = []
    cur = conn.cursor()
    cur.execute('select user_id, topic_user from user_vk_characteristic;')
    aaa = cur.fetchall()
    cur.close()
    for item in aaa:
        zxc.append(item[1])
        qwer.append(item[0])
    index = 0
    SAME_CLUB_COLOR, DIFFERENT_CLUB_COLOR = "black", "red"
    edge_attrs = {}
    G = nx.Graph()
    for _ in range(len(qwer)):
        index += 1
        G.add_node(index, theme=zxc[index - 1])
    nx.set_edge_attributes(G, edge_attrs, "blue")

    # Show with Bokeh
    plot = Plot(width=800, height=800,
                x_range=Range1d(-1.1, 1.1), y_range=Range1d(-1.1, 1.1))
    plot.title.text = "Граф"

    node_hover_tool = HoverTool(tooltips=[("index", "@index"), ("theme", "@theme")])
    plot.add_tools(node_hover_tool, BoxZoomTool(), ResetTool())

    graph_renderer = from_networkx(G, nx.spring_layout, scale=1, center=(0, 0))

    graph_renderer.node_renderer.glyph = Circle(size=15, fill_color=Spectral4[0])
    graph_renderer.edge_renderer.glyph = MultiLine(line_color="red", line_alpha=0.8, line_width=1)
    plot.renderers.append(graph_renderer)
    div2, script2 = components(plot)

    return f'''
        <html lang="en">
            <head>
                <script src="https://cdn.bokeh.org/bokeh/release/bokeh-3.0.1.min.js"></script>
                <title>Bokeh Charts</title>
                <link rel="shortcut icon" href="static\images\Logo.png">
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">
      <!-- Bootstrap Bundle JS (jsDelivr CDN) -->
      <script defer src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p" crossorigin="anonymous"></script>
    <nav class="navbar navbar-expand-md navbar-dark fixed-top bg-dark">
          <div class="collapse navbar-collapse" id="navbarCollapse">
            <ul class="navbar-nav me-auto mb-2 mb-md-0">
              <li class="nav-item">
                <a class="nav-link active" href="/">Ввод ID</a>
              </li>
              <li class="nav-item">
                <a class="nav-link active" href="/analitic">Аналитика группы</a>
              </li>
              <li class="nav-item">
                <a class="nav-link active" href="/users">Сведения об участниках</a>
              </li>
                <li class="nav-item">
                <a class="nav-link active" href="/interest">Интересы участников</a>
              </li>
            </ul>
          </div>
        </nav>
            </head>
            <body>
                {div}
                {script}
                <br><br>
                {div2}
                {script2}
            </body>
        </html>
        '''








if __name__ == '__main__':
    app.run(debug=True)
