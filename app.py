from flask import Flask, request, jsonify, send_from_directory
import language_tool_python

app = Flask(__name__, static_folder='static')
tool = language_tool_python.LanguageToolPublicAPI('fr')

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/style.css')
def style():
    return send_from_directory('static', 'style.css')

@app.route('/corriger', methods=['POST'])
def corriger():
    data = request.get_json()
    texte = data.get('texte', '')

    matches = tool.check(texte)
    texte_corrige = language_tool_python.utils.correct(texte, matches)

    texte_souligne = texte
    offset = 0
    details = []

    for m in matches:
        start = m.offset + offset
        end = start + m.errorLength
        correction = m.replacements[0] if m.replacements else ''
        texte_souligne = (texte_souligne[:start] +
                          "<span class='highlight'>" + texte_souligne[start:end] + "</span>" +
                          texte_souligne[end:])
        offset += len("<span class='highlight'></span>")

        details.append({
            "erreur": texte[m.offset:m.offset+m.errorLength],
            "suggestion": correction,
            "explication": m.message
        })

    return jsonify({
        "original": texte,
        "corrige": texte_corrige,
        "avec_soulignage": texte_souligne,
        "details": details
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
