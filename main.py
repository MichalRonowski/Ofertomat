import flet as ft
from database import Database
from importer import DataImporter
from pdf_generator import PDFGenerator
from docx_generator import DOCXGenerator
from datetime import datetime
import os

class OfertomatApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.db = Database()
        self.importer = DataImporter()
        self.pdf_gen = PDFGenerator()
        self.docx_gen = DOCXGenerator()
        
        # Dane tymczasowe dla oferty
        self.offer_items = []
        
        # Konfiguracja strony
        self.page.title = "Ofertomat"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.window_width = 2600
        self.page.window_height = 900
        self.page.window_min_width = 2400
        self.page.window_min_height = 800
        
        # Motyw kolorystyczny zgodny z logo Piwowar
        self.page.theme = ft.Theme(
            color_scheme=ft.ColorScheme(
                primary="#C8102E",  # Czerwony z logo
                on_primary="#FFFFFF",
                secondary="#8B8B8B",  # Szary z logo
                on_secondary="#FFFFFF",
            )
        )
        
        # Nawigacja
        self.rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            destinations=[
                ft.NavigationRailDestination(
                    icon="category_outlined",
                    selected_icon="category",
                    label="Kategorie"
                ),
                ft.NavigationRailDestination(
                    icon="inventory_outlined",
                    selected_icon="inventory",
                    label="Produkty"
                ),
                ft.NavigationRailDestination(
                    icon="upload_file_outlined",
                    selected_icon="upload_file",
                    label="Import"
                ),
                ft.NavigationRailDestination(
                    icon="description_outlined",
                    selected_icon="description",
                    label="Nowa Oferta"
                ),
                ft.NavigationRailDestination(
                    icon="badge_outlined",
                    selected_icon="badge",
                    label="Wizytówka"
                ),
            ],
            on_change=self.navigate
        )
        
        # Kontener na zawartość
        self.content = ft.Container(expand=True)
        
        # Layout
        self.page.add(
            ft.Row([
                self.rail,
                ft.VerticalDivider(width=1),
                self.content
            ], expand=True)
        )
        
        # Pokaż pierwszy widok
        self.show_categories_view()
    
    def navigate(self, e):
        """Nawigacja między widokami"""
        if e.control.selected_index == 0:
            self.show_categories_view()
        elif e.control.selected_index == 1:
            self.show_products_view()
        elif e.control.selected_index == 2:
            self.show_import_view()
        elif e.control.selected_index == 3:
            self.show_offer_view()
        elif e.control.selected_index == 4:
            self.show_business_card_view()
    
    # === KATEGORIE ===
    
    def show_categories_view(self):
        """Widok zarządzania kategoriami"""
        categories = self.db.get_categories()
        
        # Tabela kategorii
        rows = []
        for cat in categories:
            # Użyj partial zamiast lambda w pętli
            from functools import partial
            
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(cat['name'])),
                        ft.DataCell(ft.Text(f"{cat['default_margin']:.1f}%")),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    icon="edit",
                                    tooltip="Edytuj",
                                    data=cat,
                                    on_click=lambda e: self.edit_category(e.control.data)
                                ),
                                ft.IconButton(
                                    icon="delete",
                                    tooltip="Usuń",
                                    icon_color=ft.Colors.RED_400,
                                    data=cat,
                                    on_click=lambda e: self.delete_category(e.control.data)
                                ),
                            ])
                        ),
                    ]
                )
            )
        
        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nazwa kategorii")),
                ft.DataColumn(ft.Text("Domyślna marża")),
                ft.DataColumn(ft.Text("Akcje")),
            ],
            rows=rows,
        )
        
        self.content.content = ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.Text("Zarządzanie kategoriami", size=24, weight=ft.FontWeight.BOLD),
                    ft.FilledButton(
                        "Dodaj kategorię",
                        icon="add",
                        on_click=self.add_category_dialog
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=20
            ),
            ft.Container(
                content=table,
                padding=20
            )
        ], scroll=ft.ScrollMode.AUTO, expand=True)
        self.page.update()
    
    def add_category_dialog(self, e):
        """Dialog dodawania kategorii"""
        def close_dlg(e):
            dlg.open = False
            self.page.update()
        
        def save_category(e):
            try:
                if name_field.value and margin_field.value:
                    margin = float(margin_field.value)
                    success = self.db.add_category(name_field.value, margin)
                    if success:
                        dlg.open = False
                        self.page.update()
                        self.show_categories_view()
                        self.show_snackbar(f"Kategoria '{name_field.value}' dodana!", ft.Colors.GREEN_400)
                    else:
                        self.show_snackbar("Kategoria o tej nazwie już istnieje!", ft.Colors.RED_400)
            except ValueError:
                self.show_snackbar("Nieprawidłowa wartość marży!", ft.Colors.RED_400)
            except Exception as ex:
                print(f"Błąd dodawania kategorii: {ex}")
                self.show_snackbar(f"Błąd: {str(ex)}", ft.Colors.RED_400)
        
        name_field = ft.TextField(label="Nazwa kategorii", autofocus=True)
        margin_field = ft.TextField(label="Domyślna marża (%)", value="30", keyboard_type=ft.KeyboardType.NUMBER)
        
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Dodaj kategorię"),
            content=ft.Column([name_field, margin_field], tight=True, height=150),
            actions=[
                ft.TextButton("Anuluj", on_click=close_dlg),
                ft.FilledButton("Zapisz", on_click=save_category),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()
    
    def edit_category(self, category):
        """Dialog edycji kategorii"""
        def close_dlg(e):
            dlg.open = False
            self.page.update()
        
        def save_category(e):
            try:
                if name_field.value and margin_field.value:
                    margin = float(margin_field.value)
                    success = self.db.update_category(category['id'], name_field.value, margin)
                    if success:
                        dlg.open = False
                        self.page.update()
                        self.show_categories_view()
                        self.show_snackbar(f"Kategoria '{name_field.value}' zaktualizowana!", ft.Colors.GREEN_400)
                    else:
                        self.show_snackbar("Kategoria o tej nazwie już istnieje!", ft.Colors.RED_400)
            except ValueError:
                self.show_snackbar("Nieprawidłowa wartość marży!", ft.Colors.RED_400)
            except Exception as ex:
                print(f"Błąd edycji kategorii: {ex}")
                self.show_snackbar(f"Błąd: {str(ex)}", ft.Colors.RED_400)
        
        name_field = ft.TextField(label="Nazwa kategorii", value=category['name'])
        margin_field = ft.TextField(label="Domyślna marża (%)", value=str(category['default_margin']), keyboard_type=ft.KeyboardType.NUMBER)
        
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Edytuj kategorię"),
            content=ft.Column([name_field, margin_field], tight=True, height=150),
            actions=[
                ft.TextButton("Anuluj", on_click=close_dlg),
                ft.FilledButton("Zapisz", on_click=save_category),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()
    
    def delete_category(self, category):
        """Dialog usuwania kategorii"""
        def close_dlg(e):
            dlg.open = False
            self.page.update()
        
        def confirm_delete(e):
            try:
                self.db.delete_category(category['id'])
                dlg.open = False
                self.page.update()
                self.show_categories_view()
                self.show_snackbar(f"Kategoria '{category['name']}' usunięta!", ft.Colors.GREEN_400)
            except Exception as ex:
                print(f"Błąd usuwania kategorii: {ex}")
                self.show_snackbar(f"Błąd: {str(ex)}", ft.Colors.RED_400)
        
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Potwierdzenie"),
            content=ft.Text(f"Czy na pewno chcesz usunąć kategorię '{category['name']}'?"),
            actions=[
                ft.TextButton("Anuluj", on_click=close_dlg),
                ft.FilledButton("Usuń", on_click=confirm_delete, style=ft.ButtonStyle(bgcolor=ft.Colors.RED_400)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()
    
    # === PRODUKTY ===
    
    def show_products_view(self):
        """Widok listy produktów"""
        search_field = ft.TextField(
            label="Szukaj produktu",
            prefix_icon="search",
            on_change=self.search_products,
            expand=True
        )
        
        self.products_table_container = ft.Container(padding=20)
        self.refresh_products_table()
        
        self.content.content = ft.Column([
            ft.Container(
                content=ft.Column([
                    ft.Text("Produkty", size=24, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        search_field,
                        ft.FilledButton(
                            "Dodaj produkt",
                            icon="add",
                            on_click=self.add_product_dialog
                        ),
                    ]),
                ]),
                padding=20
            ),
            self.products_table_container
        ], scroll=ft.ScrollMode.AUTO, expand=True)
        self.page.update()
    
    def refresh_products_table(self, products=None):
        """Odświeża tabelę produktów"""
        if products is None:
            products = self.db.get_products()
        
        rows = []
        for prod in products:
            category_name = prod.get('category_name', 'Brak')
            
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(prod['code'])),
                        ft.DataCell(ft.Text(prod['name'])),
                        ft.DataCell(ft.Text(category_name if category_name else 'Brak')),
                        ft.DataCell(ft.Text(prod['unit'])),
                        ft.DataCell(ft.Text(f"{prod['purchase_price_net']:.2f} zł")),
                        ft.DataCell(ft.Text(f"{prod['vat_rate']:.0f}%")),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    icon="edit",
                                    tooltip="Edytuj",
                                    data=prod,
                                    on_click=lambda e: self.edit_product(e.control.data)
                                ),
                                ft.IconButton(
                                    icon="delete",
                                    tooltip="Usuń",
                                    icon_color=ft.Colors.RED_400,
                                    data=prod,
                                    on_click=lambda e: self.delete_product(e.control.data)
                                ),
                            ])
                        ),
                    ]
                )
            )
        
        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Kod")),
                ft.DataColumn(ft.Text("Nazwa")),
                ft.DataColumn(ft.Text("Kategoria")),
                ft.DataColumn(ft.Text("J.m.")),
                ft.DataColumn(ft.Text("Cena zakupu netto")),
                ft.DataColumn(ft.Text("VAT")),
                ft.DataColumn(ft.Text("Akcje")),
            ],
            rows=rows,
        )
        
        self.products_table_container.content = table
        self.page.update()
    
    def search_products(self, e):
        """Wyszukiwanie produktów"""
        query = e.control.value
        if query:
            products = self.db.search_products(query)
        else:
            products = self.db.get_products()
        self.refresh_products_table(products)
    
    def add_product_dialog(self, e):
        """Dialog dodawania produktu"""
        categories = self.db.get_categories()
        category_options = [ft.dropdown.Option(str(cat['id']), cat['name']) for cat in categories]
        
        code_field = ft.TextField(label="Kod/Indeks", autofocus=True)
        name_field = ft.TextField(label="Nazwa produktu")
        unit_field = ft.TextField(label="Jednostka miary", value="szt.")
        price_field = ft.TextField(label="Cena zakupu netto", value="0", keyboard_type=ft.KeyboardType.NUMBER)
        vat_field = ft.TextField(label="Stawka VAT (%)", value="23", keyboard_type=ft.KeyboardType.NUMBER)
        category_dropdown = ft.Dropdown(label="Kategoria", options=category_options)
        
        def close_dlg(e):
            dialog.open = False
            self.page.update()
        
        def save_product(e):
            if code_field.value and name_field.value:
                try:
                    cat_id = int(category_dropdown.value) if category_dropdown.value else None
                    price = float(price_field.value)
                    vat = float(vat_field.value)
                    
                    success = self.db.add_product(
                        code_field.value,
                        name_field.value,
                        unit_field.value,
                        price,
                        vat,
                        cat_id
                    )
                    if success:
                        dialog.open = False
                        self.page.update()
                        self.show_products_view()
                    else:
                        self.show_snackbar("Produkt o tym kodzie już istnieje!", ft.Colors.RED_400)
                except ValueError:
                    self.show_snackbar("Nieprawidłowe wartości w polach liczbowych!", ft.Colors.RED_400)
        
        dialog = ft.AlertDialog(
            title=ft.Text("Dodaj produkt"),
            content=ft.Column([
                code_field, name_field, unit_field, price_field, vat_field, category_dropdown
            ], tight=True, height=400),
            actions=[
                ft.TextButton("Anuluj", on_click=close_dlg),
                ft.FilledButton("Zapisz", on_click=save_product),
            ],
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def edit_product(self, product):
        """Dialog edycji produktu"""
        categories = self.db.get_categories()
        category_options = [ft.dropdown.Option(str(cat['id']), cat['name']) for cat in categories]
        
        code_field = ft.TextField(label="Kod/Indeks", value=product['code'])
        name_field = ft.TextField(label="Nazwa produktu", value=product['name'])
        unit_field = ft.TextField(label="Jednostka miary", value=product['unit'])
        price_field = ft.TextField(label="Cena zakupu netto", value=str(product['purchase_price_net']), keyboard_type=ft.KeyboardType.NUMBER)
        vat_field = ft.TextField(label="Stawka VAT (%)", value=str(product['vat_rate']), keyboard_type=ft.KeyboardType.NUMBER)
        category_dropdown = ft.Dropdown(
            label="Kategoria",
            options=category_options,
            value=str(product['category_id']) if product['category_id'] else None
        )
        
        def close_dlg(e):
            dialog.open = False
            self.page.update()
        
        def save_product(e):
            if code_field.value and name_field.value:
                try:
                    cat_id = int(category_dropdown.value) if category_dropdown.value else None
                    price = float(price_field.value)
                    vat = float(vat_field.value)
                    
                    success = self.db.update_product(
                        product['id'],
                        code_field.value,
                        name_field.value,
                        unit_field.value,
                        price,
                        vat,
                        cat_id
                    )
                    if success:
                        dialog.open = False
                        self.page.update()
                        self.show_products_view()
                    else:
                        self.show_snackbar("Produkt o tym kodzie już istnieje!", ft.Colors.RED_400)
                except ValueError:
                    self.show_snackbar("Nieprawidłowe wartości w polach liczbowych!", ft.Colors.RED_400)
        
        dialog = ft.AlertDialog(
            title=ft.Text("Edytuj produkt"),
            content=ft.Column([
                code_field, name_field, unit_field, price_field, vat_field, category_dropdown
            ], tight=True, height=400),
            actions=[
                ft.TextButton("Anuluj", on_click=close_dlg),
                ft.FilledButton("Zapisz", on_click=save_product),
            ],
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def delete_product(self, product):
        """Dialog usuwania produktu"""
        def close_dlg(e):
            dialog.open = False
            self.page.update()
        
        def confirm_delete(e):
            self.db.delete_product(product['id'])
            dialog.open = False
            self.page.update()
            self.show_products_view()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Potwierdzenie"),
            content=ft.Text(f"Czy na pewno chcesz usunąć produkt '{product['name']}'?"),
            actions=[
                ft.TextButton("Anuluj", on_click=close_dlg),
                ft.FilledButton("Usuń", on_click=confirm_delete, style=ft.ButtonStyle(bgcolor=ft.Colors.RED_400)),
            ],
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    # === IMPORT ===
    
    def show_import_view(self):
        """Widok importu danych"""
        categories = self.db.get_categories()
        category_options = [ft.dropdown.Option(str(cat['id']), cat['name']) for cat in categories]
        
        self.import_category_dropdown = ft.Dropdown(
            label="Przypisz do kategorii (opcjonalne)",
            options=category_options,
            width=300
        )
        
        self.import_file_picker = ft.FilePicker(on_result=self.on_file_picked)
        self.page.overlay.append(self.import_file_picker)
        
        self.import_status = ft.Text()
        
        self.content.content = ft.Column([
            ft.Container(
                content=ft.Column([
                    ft.Text("Import produktów", size=24, weight=ft.FontWeight.BOLD),
                    ft.Text("Importuj produkty z plików CSV lub Excel (.xlsx, .xls)"),
                    ft.Divider(),
                    ft.Text("Wymagane kolumny w pliku:", weight=ft.FontWeight.BOLD),
                    ft.Text("• Nr/Indeks/Kod - kod produktu"),
                    ft.Text("• Opis/Nazwa - nazwa produktu"),
                    ft.Text("• Podst. jednostka miary/Jednostka (opcjonalne)"),
                    ft.Text("• Ostatni koszt bezpośredni/Cena zakupu (opcjonalne)"),
                    ft.Text("• Tow. grupa księgowa VAT/VAT (opcjonalne)"),
                    ft.Divider(),
                    self.import_category_dropdown,
                    ft.FilledButton(
                        "Wybierz plik do importu",
                        icon="upload_file",
                        on_click=lambda e: self.import_file_picker.pick_files(
                            allowed_extensions=["csv", "xlsx", "xls"],
                            dialog_title="Wybierz plik do importu"
                        )
                    ),
                    self.import_status,
                ]),
                padding=20
            ),
        ], scroll=ft.ScrollMode.AUTO, expand=True)
        self.page.update()
    
    def on_file_picked(self, e: ft.FilePickerResultEvent):
        """Obsługa wybranego pliku"""
        if e.files:
            file_path = e.files[0].path
            self.import_status.value = f"Importowanie: {e.files[0].name}..."
            self.page.update()
            
            try:
                category_id = int(self.import_category_dropdown.value) if self.import_category_dropdown.value else None
                products = self.importer.import_from_file(file_path, category_id)
                added, updated = self.db.import_products_batch(products)
                
                self.import_status.value = f"✓ Import zakończony! Dodano: {added}, Zaktualizowano: {updated}"
                self.import_status.color = ft.Colors.GREEN_400
                self.show_snackbar(f"Import zakończony! Dodano: {added}, Zaktualizowano: {updated}", ft.Colors.GREEN_400)
            except Exception as ex:
                self.import_status.value = f"✗ Błąd importu: {str(ex)}"
                self.import_status.color = ft.Colors.RED_400
                self.show_snackbar(f"Błąd importu: {str(ex)}", ft.Colors.RED_400)
            
            self.page.update()
    
    # === OFERTA ===
    
    def show_offer_view(self):
        """Widok tworzenia oferty"""
        self.offer_items = []
        
        categories = self.db.get_categories()
        self.offer_category_checkboxes = []
        
        category_selection = ft.Column()
        for cat in categories:
            cb = ft.Checkbox(label=cat['name'], value=False, data=cat['id'])
            self.offer_category_checkboxes.append(cb)
            category_selection.controls.append(cb)
        
        self.offer_table_container = ft.Container()
        self.offer_title_field = ft.TextField(label="Tytuł oferty", value="Oferta handlowa", width=400)
        
        self.content.content = ft.Column([
            ft.Container(
                content=ft.Column([
                    ft.Text("Kreator oferty", size=24, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    self.offer_title_field,
                    ft.Text("Wybierz kategorie do oferty:", weight=ft.FontWeight.BOLD),
                    category_selection,
                    ft.FilledButton(
                        "Załaduj produkty z wybranych kategorii",
                        icon="add_shopping_cart",
                        on_click=self.load_offer_products
                    ),
                    ft.Divider(),
                    self.offer_table_container,
                ]),
                padding=20
            ),
        ], scroll=ft.ScrollMode.AUTO, expand=True)
        self.page.update()
    
    def load_offer_products(self, e):
        """Ładuje produkty z wybranych kategorii do oferty"""
        selected_categories = [cb.data for cb in self.offer_category_checkboxes if cb.value]
        
        if not selected_categories:
            self.show_snackbar("Wybierz przynajmniej jedną kategorię!", ft.Colors.ORANGE_400)
            return
        
        self.offer_items = []
        for cat_id in selected_categories:
            products = self.db.get_products(cat_id)
            for prod in products:
                # Debug: wypisz unit dla pierwszego produktu
                if len(self.offer_items) == 0:
                    print(f"DEBUG: Product unit = '{prod.get('unit')}' for product: {prod['name']}")
                
                self.offer_items.append({
                    'product_id': prod['id'],
                    'name': prod['name'],
                    'unit': prod.get('unit') or 'szt.',  # Obsługa NULL
                    'quantity': 1.0,
                    'purchase_price_net': prod['purchase_price_net'],
                    'vat_rate': prod['vat_rate'],
                    'margin': prod.get('default_margin', 30.0),
                    'category_name': prod.get('category_name', 'Brak')
                })
        
        self.refresh_offer_table()
    
    def refresh_offer_table(self):
        """Odświeża tabelę oferty"""
        rows = []
        for i, item in enumerate(self.offer_items):
            # Kalkulacja cen
            net_price = item['purchase_price_net'] * (1 + item['margin'] / 100)
            gross_price = net_price * (1 + item['vat_rate'] / 100)
            
            # Pole edycji nazwy
            name_field = ft.TextField(
                value=item['name'],
                multiline=True,
                min_lines=1,
                max_lines=3,
                data=i,
                on_blur=lambda e: self.update_item_name(e.control.data, e.control.value)
            )
            
            # Pole edycji J.M.
            unit_value = item.get('unit', 'szt.')
            if not unit_value:  # Jeśli None lub pusty string
                unit_value = 'szt.'
            
            print(f"DEBUG refresh_offer_table: Creating unit field for row {i}, value='{unit_value}'")
            
            unit_field = ft.TextField(
                value=unit_value,
                width=120,  # Zwiększona szerokość
                data=i,
                on_blur=lambda e: self.update_item_unit(e.control.data, e.control.value)
            )
            
            print(f"DEBUG: unit_field.value = '{unit_field.value}'")
            
            # Pole edycji marży
            margin_field = ft.TextField(
                value=str(item['margin']),
                width=100,
                keyboard_type=ft.KeyboardType.NUMBER,
                data=i,
                on_blur=lambda e: self.update_margin(e.control.data, e.control.value)
            )
            
            # Pole edycji ceny netto
            net_field = ft.TextField(
                value=f"{net_price:.2f}",
                width=100,
                keyboard_type=ft.KeyboardType.NUMBER,
                data=i,
                on_blur=lambda e: self.update_net_price(e.control.data, e.control.value)
            )
            
            # Pole edycji ceny brutto
            gross_field = ft.TextField(
                value=f"{gross_price:.2f}",
                width=100,
                keyboard_type=ft.KeyboardType.NUMBER,
                data=i,
                on_blur=lambda e: self.update_gross_price(e.control.data, e.control.value)
            )
            
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(item['category_name'])),
                        ft.DataCell(
                            ft.Container(
                                content=name_field,
                                width=350
                            )
                        ),
                        ft.DataCell(ft.Text(f"{item['purchase_price_net']:.2f} zł")),
                        ft.DataCell(
                            ft.Container(
                                content=unit_field,
                                width=120
                            )
                        ),
                        ft.DataCell(margin_field),
                        ft.DataCell(ft.Text(f"{item['vat_rate']:.0f}%")),
                        ft.DataCell(net_field),
                        ft.DataCell(gross_field),
                        ft.DataCell(
                            ft.IconButton(
                                icon="delete",
                                icon_color=ft.Colors.RED_400,
                                tooltip="Usuń",
                                data=i,
                                on_click=lambda e: self.remove_offer_item(e.control.data)
                            )
                        ),
                    ]
                )
            )
        
        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Kategoria")),
                ft.DataColumn(ft.Text("Produkt")),
                ft.DataColumn(ft.Text("Cena zakupu")),
                ft.DataColumn(ft.Text("J.M.")),
                ft.DataColumn(ft.Text("Marża %"), numeric=True),
                ft.DataColumn(ft.Text("VAT"), numeric=True),
                ft.DataColumn(ft.Text("Cena netto jedn."), numeric=True),
                ft.DataColumn(ft.Text("Cena brutto jedn."), numeric=True),
                ft.DataColumn(ft.Text("Akcje")),
            ],
            rows=rows,
            column_spacing=20,
            horizontal_margin=10,
            heading_row_height=50,
            data_row_max_height=80,
        )
        
        self.offer_table_container.content = ft.Column([
            ft.Container(
                content=ft.Row([table], scroll=ft.ScrollMode.AUTO),
                padding=10,
            ),
            ft.Divider(),
            ft.FilledButton(
                "Generuj PDF",
                icon="picture_as_pdf",
                on_click=self.generate_offer_pdf
            ) if len(self.offer_items) > 0 else ft.Container(),
        ], scroll=ft.ScrollMode.AUTO)
        self.page.update()
    
    def update_item_name(self, index, value):
        """Aktualizuje nazwę produktu w ofercie"""
        if value and value.strip():
            self.offer_items[index]['name'] = value.strip()
    
    def update_item_unit(self, index, value):
        """Aktualizuje jednostkę miary w ofercie"""
        if value and value.strip():
            self.offer_items[index]['unit'] = value.strip()
    
    def update_margin(self, index, value):
        """Aktualizuje marżę w ofercie"""
        try:
            # Zamień przecinek na kropkę dla poprawnego parsowania
            margin = float(value.replace(',', '.'))
            self.offer_items[index]['margin'] = margin
            self.refresh_offer_table()
        except ValueError:
            self.show_snackbar("Nieprawidłowa wartość marży!", ft.Colors.RED_400)
    
    def update_net_price(self, index, value):
        """Aktualizuje cenę netto i przelicza marżę"""
        try:
            # Zamień przecinek na kropkę dla poprawnego parsowania
            net_price = float(value.replace(',', '.'))
            item = self.offer_items[index]
            
            # Przelicz marżę na podstawie nowej ceny netto
            if item['purchase_price_net'] > 0:
                new_margin = ((net_price / item['purchase_price_net']) - 1) * 100
                item['margin'] = round(new_margin, 2)
                self.refresh_offer_table()
            else:
                self.show_snackbar("Cena zakupu nie może być zero!", ft.Colors.RED_400)
        except ValueError:
            self.show_snackbar("Nieprawidłowa wartość ceny netto!", ft.Colors.RED_400)
    
    def update_gross_price(self, index, value):
        """Aktualizuje cenę brutto i przelicza cenę netto oraz marżę"""
        try:
            # Zamień przecinek na kropkę dla poprawnego parsowania
            gross_price = float(value.replace(',', '.'))
            item = self.offer_items[index]
            
            # Przelicz cenę netto z brutto
            net_price = gross_price / (1 + item['vat_rate'] / 100)
            
            # Przelicz marżę na podstawie nowej ceny netto
            if item['purchase_price_net'] > 0:
                new_margin = ((net_price / item['purchase_price_net']) - 1) * 100
                item['margin'] = round(new_margin, 2)
                self.refresh_offer_table()
            else:
                self.show_snackbar("Cena zakupu nie może być zero!", ft.Colors.RED_400)
        except ValueError:
            self.show_snackbar("Nieprawidłowa wartość ceny brutto!", ft.Colors.RED_400)
    
    def remove_offer_item(self, index):
        """Usuwa pozycję z oferty"""
        self.offer_items.pop(index)
        self.refresh_offer_table()
    
    def generate_offer_pdf(self, e):
        """Generuje PDF i DOCX z oferty"""
        if not self.offer_items:
            self.show_snackbar("Brak produktów w ofercie!", ft.Colors.ORANGE_400)
            return
        
        # Przygotuj dane
        offer_data = {
            'title': self.offer_title_field.value,
            'date': datetime.now().strftime('%d.%m.%Y'),
            'items': self.offer_items,
            'business_card': self.db.get_business_card()
        }
        
        # Generuj nazwę pliku
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pdf_path = f"Oferta_{timestamp}.pdf"
        docx_path = f"Oferta_{timestamp}.docx"
        
        # Generuj oba formaty
        pdf_success = self.pdf_gen.generate_offer_pdf(offer_data, pdf_path)
        docx_success = self.docx_gen.generate_offer_docx(offer_data, docx_path)
        
        if pdf_success and docx_success:
            abs_path = os.path.abspath(pdf_path)
            self.show_snackbar(f"Oferta wygenerowana: PDF i DOCX", ft.Colors.GREEN_400)
            
            # Otwórz folder z plikiem
            os.startfile(os.path.dirname(abs_path))
        elif pdf_success:
            self.show_snackbar("PDF wygenerowany, błąd DOCX!", ft.Colors.ORANGE_400)
        elif docx_success:
            self.show_snackbar("DOCX wygenerowany, błąd PDF!", ft.Colors.ORANGE_400)
        else:
            self.show_snackbar("Błąd generowania oferty!", ft.Colors.RED_400)
    
    # === WIZYTÓWKA ===
    
    def show_business_card_view(self):
        """Wyświetla widok wizytówki użytkownika"""
        # Pobierz aktualną wizytówkę
        card = self.db.get_business_card()
        
        # Pola formularza
        company_field = ft.TextField(
            label="Firma",
            value=card['company'] if card and card.get('company') else "",
            width=400
        )
        
        name_field = ft.TextField(
            label="Imię i nazwisko",
            value=card['full_name'] if card else "",
            width=400
        )
        
        phone_field = ft.TextField(
            label="Numer telefonu",
            value=card['phone'] if card else "",
            width=400
        )
        
        email_field = ft.TextField(
            label="Adres e-mail",
            value=card['email'] if card else "",
            width=400
        )
        
        def save_card(e):
            """Zapisuje wizytówkę"""
            success = self.db.save_business_card(
                company_field.value or "",
                name_field.value or "",
                phone_field.value or "",
                email_field.value or ""
            )
            
            if success:
                self.show_snackbar("Wizytówka zapisana!", ft.Colors.GREEN_400)
            else:
                self.show_snackbar("Błąd zapisywania wizytówki!", ft.Colors.RED_400)
        
        # Layout
        self.content.content = ft.Column([
            ft.Text("Wizytówka", size=32, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Text("Dane będą wyświetlane w nagłówku każdego raportu", size=14, color=ft.Colors.GREY_700),
            ft.Container(height=20),
            company_field,
            name_field,
            phone_field,
            email_field,
            ft.Container(height=20),
            ft.FilledButton(
                "Zapisz wizytówkę",
                icon="save",
                on_click=save_card
            ),
        ], scroll=ft.ScrollMode.AUTO)
        
        self.page.update()
    
    # === POMOCNICZE ===
    
    def show_snackbar(self, message, color=None):
        """Pokazuje snackbar z wiadomością"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=color
        )
        self.page.snack_bar.open = True
        self.page.update()


def main(page: ft.Page):
    OfertomatApp(page)


if __name__ == "__main__":
    ft.app(target=main)
