"""Comprobación integral aislada: python3 -B tests/check_revision_app.py.

No copia historias/borradores ni credenciales; no genera ni envía documentos.
"""
from pathlib import Path
import os
import shutil
import sys
import tempfile

from streamlit.testing.v1 import AppTest


def ejecutar():
    root = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory(prefix='revision-documental-') as temporal:
        sandbox = Path(temporal)
        for nombre in ('app.py', 'core', 'herramientas', 'servicios', 'utils'):
            origen, destino = root / nombre, sandbox / nombre
            if origen.is_dir():
                shutil.copytree(origen, destino, ignore=shutil.ignore_patterns('__pycache__', '*.jsonl', 'borrador*', '.DS_Store'))
            else:
                shutil.copy2(origen, destino)
        (sandbox / 'data').mkdir()
        for origen in (root / 'data').iterdir():
            if origen.suffix in ('.csv', '.xls', '.xlsx'):
                shutil.copy2(origen, sandbox / 'data' / origen.name)
        (sandbox / '.streamlit').mkdir()
        (sandbox / '.streamlit/secrets.toml').write_text('openai_api_key=""\ngoogle_oauth_client_id=""\ngoogle_oauth_client_secret=""\ngoogle_oauth_redirect_uri=""\n')
        anterior = Path.cwd()
        os.chdir(sandbox)
        sys.path.insert(0, str(sandbox))
        try:
            app = AppTest.from_file(str(sandbox / 'app.py'), default_timeout=30)
            app.session_state['app_autenticada'] = True
            app.run()
            def comprobar():
                assert not app.exception, [e.message for e in app.exception]
            def generar():
                return next(b for b in app.button if b.label == 'Generar Historia Clínica')
            def confirmar():
                next(b for b in app.button if b.label.startswith('Confirmo que revisé')).click().run()
                comprobar()
            def limpiar():
                next(b for b in app.button if b.label == 'Limpiar y empezar otra historia').click().run()
                comprobar()
            comprobar()
            assert not generar().disabled
            app.selectbox(key='patologia_ejemplo_urgencias').select('NEUMONÍA').run()
            app.selectbox(key='nivel_ejemplo_urgencias').select('HOSPITALIZACIÓN').run()
            selector = app.selectbox(key='ejemplo_guia_urgencias')
            selector.select(selector.options[1]).run()
            app.button(key='ver_ejemplo_urgencias').click().run()
            comprobar()
            assert generar().disabled
            import json
            borrador = json.loads((sandbox / 'data' / 'borrador_pediatria_urgencias.json').read_text())
            assert borrador['data']['urgencias_ejemplo_origen']
            confirmar()
            assert not generar().disabled
            app.run()
            comprobar()
            assert not generar().disabled, 'La confirmación debe sobrevivir un rerun sin ediciones'
            app.text_input(key='nombre_1').set_value('PACIENTE DE PRUEBA').run()
            assert generar().disabled
            confirmar()
            assert not generar().disabled
            # Simula reinicio: se restaura procedencia del borrador, nunca la confirmación.
            app = AppTest.from_file(str(sandbox / 'app.py'), default_timeout=30)
            app.session_state['app_autenticada'] = True
            app.run()
            comprobar()
            assert generar().disabled
            limpiar()
            assert not generar().disabled
            assert not app.session_state['urgencias_ejemplo_origen']
            print('URGENCIAS: ejemplo, confirmación, edición, restauración de borrador y limpieza OK')
            for area in ('Consulta Externa', 'Pediatría Hospitalización', 'Telemedicina'):
                next(s for s in app.selectbox if s.label == 'Área de servicio').select(area).run()
                comprobar()
                assert not generar().disabled
                assert any(s.value == 'Revisión antes de generar' for s in app.subheader)
                boton = next(b for b in app.button if b.key and b.key.endswith('_ver_ejemplo'))
                # El selector de caso debe apuntar a una opción docente concreta.
                selectores = [s for s in app.selectbox if s.key and 'ejemplo' in s.key]
                for selector in selectores:
                    if 'guia' in selector.key and len(selector.options) > 1:
                        selector.select(selector.options[1]).run()
                boton.click().run()
                comprobar()
                assert generar().disabled, f'{area}: ejemplo sin marcar'
                confirmar()
                assert not generar().disabled
                app.run()
                comprobar()
                assert not generar().disabled
                limpiar()
                assert not generar().disabled
                print(f'{area}: panel, ejemplo, confirmación y limpieza OK')
        finally:
            os.chdir(anterior)
            sys.path.remove(str(sandbox))


if __name__ == '__main__':
    ejecutar()
