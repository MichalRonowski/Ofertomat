import flet as ft

def main(page: ft.Page):
    page.title = "Test Dialog"
    
    def show_dialog(e):
        print("Kliknięto przycisk!")
        
        def close_dlg(e):
            dlg.open = False
            page.update()
        
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Test"),
            content=ft.Text("Dialog działa!"),
            actions=[
                ft.TextButton("OK", on_click=close_dlg)
            ],
        )
        
        page.overlay.append(dlg)
        dlg.open = True
        page.update()
    
    page.add(
        ft.ElevatedButton("Pokaż dialog", on_click=show_dialog)
    )

ft.app(target=main)
