import re

with open('portfolio.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add PWA tags and D3
head_replacement = """<link rel="manifest" href="./manifest.json">
<meta name="theme-color" content="#070B0A">
<link rel="apple-touch-icon" href="linkedin_banner_light_2x (8).png">
<title>Geletaw Sahle — AI Research &amp; Neurotechnology</title>
<script src="https://d3js.org/d3.v7.min.js"></script>"""
content = content.replace('<title>Geletaw Sahle — AI Research &amp; Neurotechnology</title>', head_replacement)

# 2. Replace CSS
css_target = """.svg-container{
    flex:1;height:100%;
    display:flex;align-items:center;justify-content:center;
    padding:40px;
    transition:all 0.55s cubic-bezier(0.16,1,0.3,1);
    overflow:auto;
  }

  svg{ width:100%;height:100%;max-height:100vh;display:block;min-width:1100px; }

  .interactive-node{ cursor:pointer; outline:none; }
  .interactive-node circle{ transition:all 0.25s ease; }
  .interactive-node text{ transition:all 0.25s ease; }

  @keyframes node-pulse{
    0%{ stroke-width:1.2; stroke-opacity:0.55; }
    50%{ stroke-width:4.5; stroke-opacity:0.08; }
    100%{ stroke-width:1.2; stroke-opacity:0.55; }
  }
  .interactive-node .pulse-ring{
    animation:node-pulse 2.6s infinite;
    stroke:var(--teal);
    fill:none;
  }

  .interactive-node:hover circle.core,
  .interactive-node.active-node circle.core,
  .interactive-node:focus-visible circle.core{
    fill:var(--teal) !important;
    stroke:var(--amber) !important;
    stroke-width:2 !important;
  }
  .interactive-node:hover text,
  .interactive-node.active-node text,
  .interactive-node:focus-visible text{
    fill:var(--ink) !important;
    font-weight:600 !important;
  }
  .interactive-node:focus-visible .pulse-ring{
    stroke:var(--amber);
  }"""

css_replacement = """.svg-container{
    flex:1;height:100%;
    position:relative;
    transition:all 0.55s cubic-bezier(0.16,1,0.3,1);
    overflow:hidden;
  }
  #d3-canvas { width:100%; height:100%; display:block; cursor:grab; outline:none; }
  #d3-canvas:active { cursor:grabbing; }
  .node { cursor:pointer; outline:none; }
  .node circle { transition: fill 0.2s, stroke 0.2s, stroke-width 0.2s; }
  .node text { transition: fill 0.2s, font-weight 0.2s; pointer-events:none; }
  .node:hover circle.core, .node.active-node circle.core { fill:var(--teal)!important; stroke:var(--amber)!important; stroke-width:2!important; }
  .node:hover text, .node.active-node text { fill:var(--ink)!important; font-weight:600!important; }
  .link { stroke:var(--teal); stroke-opacity:0.2; stroke-width:1.5px; }
  @keyframes node-pulse{ 0%{ stroke-width:1.2; stroke-opacity:0.55; } 50%{ stroke-width:5; stroke-opacity:0.1; } 100%{ stroke-width:1.2; stroke-opacity:0.55; } }
  .pulse-ring { animation:node-pulse 2.6s infinite; stroke:var(--teal); fill:none; }"""

content = content.replace(css_target, css_replacement)

# 3. Replace SVG block
svg_pattern = re.compile(r'<div class="svg-container">\s*<svg id="banner".*?</svg>\s*</div>', re.DOTALL)
svg_replacement = """<div class="svg-container">
      <svg id="d3-canvas" role="img" aria-label="Interactive Network Diagram"></svg>
    </div>"""
content = svg_pattern.sub(svg_replacement, content)

# 4. Inject D3 logic
d3_script = """

  // ---- D3 GRAPH LOGIC ----
  const d3Canvas = d3.select("#d3-canvas");
  const svgGroup = d3Canvas.append("g");

  // Setup Zoom & Pan
  const zoom = d3.zoom()
    .scaleExtent([0.3, 3])
    .on("zoom", (event) => {
      svgGroup.attr("transform", event.transform);
    });
  d3Canvas.call(zoom);

  let graphNodes = [
    { id: 'HUB', title: 'AI', type: 'hub', radius: 15 },
    { id: 'agents', title: 'AGENTS', type: 'domain', radius: 6, pulse: true },
    { id: 'research', title: 'RESEARCH', type: 'domain', radius: 6, pulse: true },
    { id: 'data-scientist', title: 'DATA SCIENTIST', type: 'domain', radius: 6, pulse: true },
    { id: 'digital-health', title: 'DIGITAL HEALTH', type: 'domain', radius: 6, pulse: true },
    { id: 'neurotech', title: 'NEUROTECHNOLOGY', type: 'domain', radius: 6, pulse: true },
    { id: 'connect', title: 'CONNECT', type: 'domain', radius: 6, color: '#FFB454' }
  ];

  let graphLinks = [
    { source: 'HUB', target: 'agents' },
    { source: 'HUB', target: 'research' },
    { source: 'HUB', target: 'data-scientist' },
    { source: 'HUB', target: 'digital-health' },
    { source: 'HUB', target: 'neurotech' },
    { source: 'HUB', target: 'connect' }
  ];

  // Populate leaves from nodeDB
  Object.keys(nodeDB).forEach(key => {
    const item = nodeDB[key];
    if(item.type === 'leaf' || item.parent) {
      if(!graphNodes.find(n => n.id === key)){
        graphNodes.push({ id: key, title: item.title, type: item.type, radius: 3.2 });
      }
      if(item.parent) {
        graphLinks.push({ source: item.parent, target: key });
      }
    }
  });

  // Connect manual leaf links
  [
    { id: 'connect-gh', title: 'GITHUB', parent: 'connect', url: '#TODO_UPDATE_GH_LINK' },
    { id: 'connect-gs', title: 'GOOGLE SCHOLAR', parent: 'connect', url: '#TODO_UPDATE_SCHOLAR_LINK' },
    { id: 'connect-cv', title: 'CV / RESUME', parent: 'connect', url: '#TODO_UPDATE_CV_LINK' }
  ].forEach(n => {
    graphNodes.push({ id: n.id, title: n.title, type: 'leaf', radius: 3.2, color: '#FFB454', url: n.url });
    graphLinks.push({ source: n.parent, target: n.id });
  });

  // Initialize Force Simulation
  const width = d3Canvas.node().clientWidth;
  const height = d3Canvas.node().clientHeight;
  
  const simulation = d3.forceSimulation(graphNodes)
    .force("link", d3.forceLink(graphLinks).id(d => d.id).distance(d => {
      if(d.source.id === 'HUB') return 180;
      return 100;
    }))
    .force("charge", d3.forceManyBody().strength(-300))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("collide", d3.forceCollide().radius(40));

  // Draw links
  const link = svgGroup.append("g")
    .selectAll("line")
    .data(graphLinks)
    .join("line")
    .attr("class", "link");

  // Draw nodes
  const node = svgGroup.append("g")
    .selectAll("g")
    .data(graphNodes)
    .join("g")
    .attr("class", "node")
    .attr("data-target", d => d.type !== 'hub' ? (d.id.startsWith('connect-') ? '' : d.id) : '')
    .call(d3.drag()
      .on("start", dragstarted)
      .on("drag", dragged)
      .on("end", dragended));

  node.on("click", (event, d) => {
    if(d.url) { window.open(d.url, '_blank'); return; }
    if(d.type === 'hub') return;
    if(userHint) userHint.classList.add('hidden');
    
    document.querySelectorAll('.node').forEach(n => n.classList.remove('active-node'));
    event.currentTarget.classList.add('active-node');
    openPanel(d.id, event.currentTarget);
  });

  // Pulse rings for domains
  node.filter(d => d.pulse).append("circle")
    .attr("class", "pulse-ring")
    .attr("r", 9);

  // Core circles
  node.append("circle")
    .attr("class", "core")
    .attr("r", d => d.radius)
    .attr("fill", "#0B1412")
    .attr("stroke", d => d.color || "#4FD8C4")
    .attr("stroke-width", d => d.type === 'hub' ? 1.5 : 1.2);
    
  // Center dot for HUB
  node.filter(d => d.type === 'hub').append("circle")
    .attr("r", 22)
    .attr("fill", "none")
    .attr("stroke", "#FFB454")
    .attr("opacity", 0.4);

  node.append("text")
    .text(d => d.title)
    .attr("dy", d => d.type === 'hub' ? 4 : (d.type === 'domain' ? -15 : 15))
    .attr("text-anchor", "middle")
    .attr("font-family", "JetBrains Mono, monospace")
    .attr("font-size", d => d.type === 'hub' ? "12px" : (d.type === 'domain' ? "14px" : "11px"))
    .attr("fill", d => d.color || (d.type === 'domain' ? "#E9F3EF" : "#7E9C93"));

  simulation.on("tick", () => {
    link
      .attr("x1", d => d.source.x)
      .attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x)
      .attr("y2", d => d.target.y);

    node.attr("transform", d => `translate(${d.x},${d.y})`);
  });

  // Center the view on initial load
  d3Canvas.call(zoom.transform, d3.zoomIdentity.translate(width/2, height/2).scale(0.8).translate(-width/2, -height/2));

  function dragstarted(event) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    event.subject.fx = event.subject.x;
    event.subject.fy = event.subject.y;
  }
  function dragged(event) {
    event.subject.fx = event.x;
    event.subject.fy = event.y;
  }
  function dragended(event) {
    if (!event.active) simulation.alphaTarget(0);
    event.subject.fx = null;
    event.subject.fy = null;
  }

  // Handle window resize
  window.addEventListener('resize', () => {
    const w = d3Canvas.node().clientWidth;
    const h = d3Canvas.node().clientHeight;
    simulation.force("center", d3.forceCenter(w / 2, h / 2));
    simulation.alpha(0.3).restart();
  });
  
  // Service Worker Registration
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('./sw.js').then(registration => {
        console.log('SW registered: ', registration);
      }).catch(registrationError => {
        console.log('SW registration failed: ', registrationError);
      });
    });
  }
"""
content = content.replace("let lastFocusedNode = null;", "let lastFocusedNode = null;" + d3_script)

with open('portfolio.html', 'w', encoding='utf-8') as f:
    f.write(content)
