from fastapi.responses import FileResponse
from nicegui import app, ui

@app.get('/source')
def data():
    return FileResponse(path=__file__, filename=__file__)

ui.button('Download source', on_click=lambda: ui.open('/source'))
ui.button('Notify', on_click=lambda: ui.notify('test'))

ui.run()