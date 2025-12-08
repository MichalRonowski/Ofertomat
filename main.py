import flet as ft
from database import Database
from importer import DataImporter
from pdf_generator import PDFGenerator
from datetime import datetime
import os

class OfertomatApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.db = Database()
        self.importer = DataImporter()
        self.pdf_gen = PDFGenerator()
        
        # Dane tymczasowe dla oferty
        self.offer_items = []
        
        # Konfiguracja strony
        self.page.title = "Ofertomat"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.window_width = 1200
        self.page.window_height = 800
        
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
        print("DEBUG: add_category_dialog wywołane")
        
        def close_dlg(e):
            dlg.open = False
            self.page.update()
        
        def save_category(e):
            try:
                print(f"DEBUG: save_category - name={name_field.value}, margin={margin_field.value}")
                if name_field.value and margin_field.value:
                    success = self.db.add_category(name_field.value, float(margin_field.value))
                    if success:
                        dlg.open = False
                        self.page.update()
                        self.show_categories_view()
                        self.show_snackbar(f"Kategoria '{name_field.value}' dodana!", ft.Colors.GREEN_400)
                    else:
                        self.show_snackbar("Kategoria o tej nazwie już istnieje!", ft.Colors.RED_400)
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
        
        self.page.dialog = dlg
        dlg.open = True
        print(f"DEBUG: Dialog ustawiony, open={dlg.open}")
        self.page.update()
        print("DEBUG: Page zaktualizowane")
    
    def edit_category(self, category):
        """Dialog edycji kategorii"""
        print(f"DEBUG: edit_category wywołane dla: {category}")
        
        def close_dlg(e):
            dlg.open = False
            self.page.update()
        
        def save_category(e):
            try:
                if name_field.value and margin_field.value:
                    success = self.db.update_category(category['id'], name_field.value, float(margin_field.value))
                    if success:
                        dlg.open = False
                        self.page.update()
                        self.show_categories_view()
                        self.show_snackbar(f"Kategoria '{name_field.value}' zaktualizowana!", ft.Colors.GREEN_400)
                    else:
                        self.show_snackbar("Kategoria o tej nazwie już istnieje!", ft.Colors.RED_400)
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
        
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()
    
    def delete_category(self, category):
        """Dialog usuwania kategorii"""
        print(f"DEBUG: delete_category wywołane dla: {category}")
        
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
        
        self.page.dialog = dlg
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
        
        def save_product(e):
            if code_field.value and name_field.value:
                cat_id = int(category_dropdown.value) if category_dropdown.value else None
                success = self.db.add_product(
                    code_field.value,
                    name_field.value,
                    unit_field.value,
                    float(price_field.value),
                    float(vat_field.value),
                    cat_id
                )
                if success:
                    self.page.dialog.open = False
                    self.page.update()
                    self.show_products_view()
                else:
                    self.show_snackbar("Produkt o tym kodzie już istnieje!", ft.Colors.RED_400)
        
        dialog = ft.AlertDialog(
            title=ft.Text("Dodaj produkt"),
            content=ft.Column([
                code_field, name_field, unit_field, price_field, vat_field, category_dropdown
            ], tight=True, height=400),
            actions=[
                ft.TextButton("Anuluj", on_click=lambda e: self.close_dialog()),
                ft.FilledButton("Zapisz", on_click=save_product),
            ],
        )
        
        self.page.dialog = dialog
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
        
        def save_product(e):
            if code_field.value and name_field.value:
                cat_id = int(category_dropdown.value) if category_dropdown.value else None
                success = self.db.update_product(
                    product['id'],
                    code_field.value,
                    name_field.value,
                    unit_field.value,
                    float(price_field.value),
                    float(vat_field.value),
                    cat_id
                )
                if success:
                    self.page.dialog.open = False
                    self.page.update()
                    self.show_products_view()
                else:
                    self.show_snackbar("Produkt o tym kodzie już istnieje!", ft.Colors.RED_400)
        
        dialog = ft.AlertDialog(
            title=ft.Text("Edytuj produkt"),
            content=ft.Column([
                code_field, name_field, unit_field, price_field, vat_field, category_dropdown
            ], tight=True, height=400),
            actions=[
                ft.TextButton("Anuluj", on_click=lambda e: self.close_dialog()),
                ft.FilledButton("Zapisz", on_click=save_product),
            ],
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def delete_product(self, product):
        """Dialog usuwania produktu"""
        def confirm_delete(e):
            self.db.delete_product(product['id'])
            self.page.dialog.open = False
            self.page.update()
            self.show_products_view()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Potwierdzenie"),
            content=ft.Text(f"Czy na pewno chcesz usunąć produkt '{product['name']}'?"),
            actions=[
                ft.TextButton("Anuluj", on_click=lambda e: self.close_dialog()),
                ft.FilledButton("Usuń", on_click=confirm_delete, style=ft.ButtonStyle(bgcolor=ft.Colors.RED_400)),
            ],
        )
        
        self.page.dialog = dialog
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
                self.offer_items.append({
                    'product_id': prod['id'],
                    'name': prod['name'],
                    'unit': prod['unit'],
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
            
            quantity_field = ft.TextField(
                value=str(item['quantity']),
                width=80,
                keyboard_type=ft.KeyboardType.NUMBER,
                data=i,
                on_change=lambda e: self.update_quantity(e.control.data, e.control.value)
            )
            
            margin_field = ft.TextField(
                value=str(item['margin']),
                width=80,
                keyboard_type=ft.KeyboardType.NUMBER,
                data=i,
                on_change=lambda e: self.update_margin(e.control.data, e.control.value)
            )
            
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(item['category_name'])),
                        ft.DataCell(ft.Text(item['name'])),
                        ft.DataCell(quantity_field),
                        ft.DataCell(ft.Text(item['unit'])),
                        ft.DataCell(margin_field),
                        ft.DataCell(ft.Text(f"{net_price:.2f} zł")),
                        ft.DataCell(ft.Text(f"{item['vat_rate']:.0f}%")),
                        ft.DataCell(ft.Text(f"{gross_price:.2f} zł")),
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
                ft.DataColumn(ft.Text("Ilość")),
                ft.DataColumn(ft.Text("J.m.")),
                ft.DataColumn(ft.Text("Marża %")),
                ft.DataColumn(ft.Text("Cena netto jedn.")),
                ft.DataColumn(ft.Text("VAT")),
                ft.DataColumn(ft.Text("Cena brutto jedn.")),
                ft.DataColumn(ft.Text("Akcje")),
            ],
            rows=rows,
        )
        
        self.offer_table_container.content = ft.Column([
            table,
            ft.Divider(),
            ft.FilledButton(
                "Generuj PDF",
                icon="picture_as_pdf",
                on_click=self.generate_offer_pdf
            ) if len(self.offer_items) > 0 else ft.Container(),
        ])
        self.page.update()
    
    def update_quantity(self, index, value):
        """Aktualizuje ilość w ofercie"""
        try:
            self.offer_items[index]['quantity'] = float(value)
            self.refresh_offer_table()
        except ValueError:
            pass
    
    def update_margin(self, index, value):
        """Aktualizuje marżę w ofercie"""
        try:
            self.offer_items[index]['margin'] = float(value)
            self.refresh_offer_table()
        except ValueError:
            pass
    
    def remove_offer_item(self, index):
        """Usuwa pozycję z oferty"""
        self.offer_items.pop(index)
        self.refresh_offer_table()
    
    def generate_offer_pdf(self, e):
        """Generuje PDF z oferty"""
        if not self.offer_items:
            self.show_snackbar("Brak produktów w ofercie!", ft.Colors.ORANGE_400)
            return
        
        # Przygotuj dane
        offer_data = {
            'title': self.offer_title_field.value,
            'date': datetime.now().strftime('%d.%m.%Y'),
            'items': self.offer_items
        }
        
        # Generuj nazwę pliku
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f"Oferta_{timestamp}.pdf"
        
        # Generuj PDF
        success = self.pdf_gen.generate_offer_pdf(offer_data, output_path)
        
        if success:
            abs_path = os.path.abspath(output_path)
            self.show_snackbar(f"PDF wygenerowany: {abs_path}", ft.Colors.GREEN_400)
            
            # Otwórz folder z plikiem
            os.startfile(os.path.dirname(abs_path))
        else:
            self.show_snackbar("Błąd generowania PDF!", ft.Colors.RED_400)
    
    # === POMOCNICZE ===
    
    def close_dialog(self):
        """Zamyka dialog"""
        self.page.dialog.open = False
        self.page.update()
    
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
