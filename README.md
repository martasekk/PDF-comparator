<!--
  README for: PDF Comparator (PySide6)
  Drop this into README.md — GitHub will render HTML nicely.
-->

<div align="center">

<h1>🧭 PDF Comparator (PySide6)</h1>

<p>
<strong>PDF diff viewer</strong> with side-by-side pages, text extraction, and visual highlights
for <em>added</em> (green) and <em>removed</em> (red) content. Built with <strong>PySide6 / Qt</strong>.
</p>

<p>
  <a href="#-features"><img alt="Features" src="https://img.shields.io/badge/Features-rich-2ea44f?logo=qt"></a>
  <a href="#-quickstart"><img alt="Python" src="https://img.shields.io/badge/python-3.10%2B-blue.svg?logo=python"></a>
  <a href="#-license"><img alt="License" src="https://img.shields.io/badge/License-MIT-purple.svg"></a>
</p>

</div>
<hr/>

<h2 id="-features">Features</h2>

<ul>
  <li><strong>Side-by-side render</strong> with independent smooth scrolling (left/right viewers).</li>
  <li><strong>Clickable diff cards</strong> grouped by page; jump directly to a bounding box (bbox) on click.</li>
  <li><strong>Visual highlights</strong>:
    <ul>
      <li><span style="color:#cc0000">Removed (Left)</span> → red overlay</li>
      <li><span style="color:#00aa00">Added (Right)</span> → green overlay</li>
    </ul>
  </li>
  <li><strong>Multiple comparison engines</strong> (selectable in a ComboBox):
    <ul>
      <li>Myers Diff (Default)</li>
      <li>DeepDiff</li>
      <li>SequenceMatcher</li>
      <li>Hirschberg (LCS)</li>
    </ul>
  </li>
  <li><strong>Structured diff data</strong>: <code>(page, bbox, text, change_type)</code></li>
  <li><strong>Clean UI</strong> from Qt Designer (<code>Ui_MainWindow</code>) and modular <code>PDFWorker</code> / <code>PDFViewer</code> architecture.</li>
</ul>

<hr/>

<h2 id="-quickstart">🚀 Quickstart</h2>

<details open>
<summary><strong>1) Prerequisites</strong></summary>
<ul>
  <li>Python 3.10+</li>
  <li>System Qt dependencies (PySide6 wheels include Qt libraries for most platforms)</li>
</ul>
</details>

<details open>
<summary><strong>2) Install</strong></summary>

<pre><code class="language-bash">git clone https://github.com/&lt;your-org&gt;/pdf-comparator.git
cd pdf-comparator
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -U pip wheel
pip install -r requirements.txt
# If you don't have requirements.txt yet:
pip install PySide6
</code></pre>
</details>

<details open>
<summary><strong>3) Run</strong></summary>

<hr/>

<h2 id="-ui-overview">🖼️ UI Overview</h2>

<ul>
  <li><strong>Left panel:</strong> PDF viewer + Load button</li>
  <li><strong>Right panel:</strong> PDF viewer + Load button</li>
  <li><strong>Top toolbar:</strong> Compare button, Previous/Next diff, Compare-method ComboBox</li>
  <li><strong>Right side (scroll area):</strong> Diff cards grouped by page</li>
</ul>

<hr/>

<h2 id="-architecture">Files</h2>

<pre><code class="language-text">.
├─ ui/
│  └─ ui_mainwindow.py         # Generated from Qt Designer (.ui)
├─ src/
│  ├─ pdfworker.py             # Text extraction + comparison logic
│  ├─ pdfviewer.py             # QWidgets that render PDF pages and highlights
│  ├─ pdfdto.py                # Data transfer object for pdf 
│  └─ pdfcomparator.py         # Main class holding everything together 
└─ app.py / main.py            # App entrypoint
  
</code></pre>

<h3>Core classes</h3>

<ul>
  <li><code>PDFComparator(QMainWindow, Ui_MainWindow)</code>
    <ul>
      <li>Wires Designer UI, creates <code>PDFViewer</code> (left/right) + <code>PDFWorker</code></li>
      <li>Handles file open, comparison, navigation, and populates diff list</li>
    </ul>
  </li>
  <li><code>PDFWorker</code>
    <ul>
      <li><code>LoadPDF_Left(path)</code>, <code>LoadPDF_Right(path)</code></li>
      <li><code>compare_pdf()</code> → populates:
        <ul>
          <li><code>removed_diffs</code> (left), <code>added_diffs</code> (right)</li>
          <li><code>_differences</code>: list of <code>(page, bbox, text, change_type)</code></li>
          <li><code>pdfDTOLeft</code>, <code>pdfDTORight</code> (rendering payloads)</li>
          <li><code>_allCompareMethods</code> &amp; <code>_selectedCompareMethod</code></li>
        </ul>
      </li>
    </ul>
  </li>
  <li><code>PDFViewer</code>
    <ul>
      <li><code>load_pdf(path)</code>, <code>draw_pdf(pdf_data)</code>, <code>clear_pdf()</code></li>
      <li><code>highlight_differences(diffs, pdfDTO, color=(r,g,b))</code></li>
      <li><code>smooth_scroll_to_bbox(page, bbox)</code></li>
    </ul>
  </li>
</ul>

<hr/>

<h2 id="-how-comparison-works">🧪 How Comparison Works</h2>

<ol>
  <li><strong>Load PDFs</strong> → <code>PDFWorker.LoadPDF_Left/Right</code></li>
  <li><strong>Extract text + layout</strong> → per page text blocks with bounding boxes</li>
  <li><strong>Compare</strong> → selected method (Myers / DeepDiff / SequenceMatcher / Hirschberg)</li>
  <li><strong>Build diffs</strong> → tuples <code>(page, bbox, text, change_type)</code></li>
  <li><strong>Render</strong>
    <ul>
      <li>Left viewer: removed (red)</li>
      <li>Right viewer: added (green)</li>
      <li>Right panel: diff cards grouped by page, clickable</li>
    </ul>
  </li>
</ol>

<p><em>Tip:</em> You can pre- and post-process tokens (e.g., words vs. lines), normalize whitespace/case, or add a two-pass diff (line → word) for nicer highlights.</p>

<hr/>


<hr/>

<h2 id="-configuration--extensibility">Configuration &amp; Extensibility</h2>

<ul>
  <li><strong>Compare methods:</strong> register new engines in <code>PDFWorker._allCompareMethods</code> and wire to the ComboBox.</li>
  <li><strong>Tokenization:</strong> switch between char/word/line levels before passing text to the comparer.</li>
  <li><strong>Performance:</strong> cache page text/boxes; batch render; only refresh visible pages.</li>
  <li><strong>Theming:</strong> the diff cards use a small stylesheet; tweak colors in <code>populate_diff_view()</code>.</li>
</ul>


<h2 id="-ack">Acknowledgements</h2>
<ul>
  <li>Qt / PySide6 team</li>
  <li>Diff algorithms: Myers, Hirschberg (LCS), difflib/SequenceMatcher, DeepDiff</li>
</ul>

<hr/>
