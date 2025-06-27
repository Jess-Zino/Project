import { WebView } from "react-native-webview";

export default function LiveKaTeXView({ value }) {
  const html = `
    <html>
      <head>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.7/dist/katex.min.css">
        <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.7/dist/katex.min.js"></script>
      </head>
      <body style="margin:0;padding:10px;background:#222;color:white;font-size:50px;">
        <div id="math"></div>
        <script>
          window.onload = function() {
            try {
              document.getElementById("math").innerHTML = katex.renderToString(${JSON.stringify(
                value
              )}, { throwOnError: false });
            } catch (e) {
              document.getElementById("math").innerText = 'Render error: ' + e.message;
            }
          };
        </script>
      </body>
    </html>
  `;

  return (
    <WebView
      key={value}
      originWhitelist={["*"]}
      source={{ html }}
      style={{ height: 100, backgroundColor: "transparent" }}
    />
  );
}
