from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime
from typing import List, Dict
import os

class PDFGenerator:
    """Klasa do generowania raportów PDF z ofert"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        
        # Rejestruj czcionkę obsługującą Unicode (polskie znaki)
        try:
            # Pobierz ścieżkę do systemowych czcionek Windows
            import winreg
            import pathlib
            
            # Znajdź katalog czcionek Windows
            fonts_dir = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts')
            
            # Użyj Arial Unicode MS lub Arial - obie obsługują polskie znaki
            arial_path = os.path.join(fonts_dir, 'arial.ttf')
            arial_bold_path = os.path.join(fonts_dir, 'arialbd.ttf')
            
            if os.path.exists(arial_path):
                pdfmetrics.registerFont(TTFont('ArialUnicode', arial_path))
                self.font_name = 'ArialUnicode'
            else:
                self.font_name = 'Helvetica'
                
            if os.path.exists(arial_bold_path):
                pdfmetrics.registerFont(TTFont('ArialUnicode-Bold', arial_bold_path))
                self.font_bold = 'ArialUnicode-Bold'
            else:
                self.font_bold = 'Helvetica-Bold'
                
        except Exception as e:
            print(f"Nie można załadować czcionki Arial: {e}")
            self.font_name = 'Helvetica'
            self.font_bold = 'Helvetica-Bold'
        
        # Dodaj niestandardowe style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            fontName=self.font_bold,
            textColor=colors.HexColor('#8B8B8B'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='CategoryHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            fontName=self.font_bold,
            textColor=colors.HexColor('#C8102E'),
            spaceAfter=10,
            spaceBefore=20,
            leftIndent=0
        ))
        
        self.styles.add(ParagraphStyle(
            name='TableText',
            parent=self.styles['Normal'],
            fontSize=8,
            fontName=self.font_name,
            leading=10
        ))
    
    def calculate_price(self, purchase_price: float, margin: float, vat_rate: float, quantity: float = 1):
        """
        Kalkuluje ceny
        
        Returns:
            dict z kluczami: net_unit, gross_unit, net_total, vat_amount, gross_total
        """
        # Cena jednostkowa netto sprzedaży
        net_unit = purchase_price * (1 + margin / 100)
        
        # Cena jednostkowa brutto
        gross_unit = net_unit * (1 + vat_rate / 100)
        
        # Wartości dla ilości
        net_total = net_unit * quantity
        vat_amount = net_total * (vat_rate / 100)
        gross_total = net_total + vat_amount
        
        return {
            'net_unit': round(net_unit, 2),
            'gross_unit': round(gross_unit, 2),
            'net_total': round(net_total, 2),
            'vat_amount': round(vat_amount, 2),
            'gross_total': round(gross_total, 2)
        }
    
    def generate_offer_pdf(self, offer_data: Dict, output_path: str) -> bool:
        """
        Generuje PDF z ofertą
        
        Args:
            offer_data: Słownik z danymi oferty:
                - title: str (tytuł oferty)
                - date: str (data, opcjonalnie)
                - items: List[Dict] - produkty z polami:
                    - name: str
                    - quantity: float
                    - purchase_price_net: float
                    - vat_rate: float
                    - margin: float (z kategorii)
                    - category_name: str
            output_path: Ścieżka do pliku wyjściowego PDF
        
        Returns:
            bool - True jeśli sukces
        """
        try:
            # Stwórz katalog jeśli nie istnieje
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
            
            # Utwórz dokument
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            # Elementy dokumentu
            elements = []
            
            # Logo w nagłówku (jeśli istnieje)
            logo_path = 'logo_piwowar.png'
            if os.path.exists(logo_path):
                try:
                    logo = Image(logo_path, width=8*cm, height=3*cm, kind='proportional')
                    logo.hAlign = 'CENTER'
                    elements.append(logo)
                    elements.append(Spacer(1, 10))
                except Exception as e:
                    print(f"Nie można załadować logo: {e}")
            
            # Wizytówka (jeśli podana)
            business_card = offer_data.get('business_card')
            if business_card and (business_card.get('full_name') or business_card.get('phone') or business_card.get('email')):
                card_text = []
                if business_card.get('full_name'):
                    card_text.append(business_card['full_name'])
                if business_card.get('phone'):
                    card_text.append(f"Tel: {business_card['phone']}")
                if business_card.get('email'):
                    card_text.append(f"E-mail: {business_card['email']}")
                
                card_para = Paragraph(" | ".join(card_text), self.styles['Normal'])
                elements.append(card_para)
                elements.append(Spacer(1, 10))
            
            # Tytuł
            title = offer_data.get('title', 'Oferta handlowa')
            elements.append(Paragraph(title, self.styles['CustomTitle']))
            
            # Data
            date_str = offer_data.get('date', datetime.now().strftime('%d.%m.%Y'))
            date_para = Paragraph(f"Data: {date_str}", self.styles['Normal'])
            elements.append(date_para)
            elements.append(Spacer(1, 20))
            
            # Pogrupuj produkty po kategoriach
            items_by_category = {}
            for item in offer_data.get('items', []):
                category = item.get('category_name', 'Bez kategorii')
                if category not in items_by_category:
                    items_by_category[category] = []
                items_by_category[category].append(item)
            
            # Suma całkowita
            grand_total_net = 0
            grand_total_gross = 0
            
            # Dla każdej kategorii
            for category_name, items in sorted(items_by_category.items()):
                # Nagłówek kategorii
                elements.append(Paragraph(category_name, self.styles['CategoryHeader']))
                
                # Tabela produktów
                table_data = [
                    ['Nazwa', 'Cena netto', 'J.M.', 'VAT', 'Cena brutto']
                ]
                
                category_total_net = 0
                category_total_gross = 0
                
                for item in items:
                    prices = self.calculate_price(
                        item['purchase_price_net'],
                        item['margin'],
                        item['vat_rate'],
                        item['quantity']
                    )
                    
                    category_total_net += prices['net_total']
                    category_total_gross += prices['gross_total']
                    
                    # Użyj Paragraph dla nazwy aby obsługiwać długie teksty
                    name_para = Paragraph(item['name'], self.styles['TableText'])
                    
                    table_data.append([
                        name_para,
                        f"{prices['net_unit']:.2f}",
                        f"zł/{item.get('unit', 'szt.')}",
                        f"{item['vat_rate']:.0f}%",
                        f"{prices['gross_unit']:.2f} zł"
                    ])
                
                grand_total_net += category_total_net
                grand_total_gross += category_total_gross
                
                # Stwórz tabelę - dostosowane szerokości kolumn
                table = Table(table_data, colWidths=[9*cm, 2.5*cm, 2*cm, 1.5*cm, 2.5*cm])
                
                # Stylizacja tabeli
                table.setStyle(TableStyle([
                    # Nagłówek
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#C8102E')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), self.font_bold),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    
                    # Dane
                    ('FONTNAME', (0, 1), (-1, -1), self.font_name),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                    ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    
                    # Siatka
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    
                    # Padding
                    ('TOPPADDING', (0, 1), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ]))
                
                elements.append(table)
                elements.append(Spacer(1, 15))
            
            # Informacja o ważności oferty
            elements.append(Spacer(1, 20))
            validity_style = ParagraphStyle(
                name='Validity',
                parent=self.styles['Normal'],
                fontSize=8,
                fontName=self.font_name,
                textColor=colors.grey,
                alignment=TA_LEFT
            )
            validity_text = "<i>Oferta ważna w dniu przedstawienia do momentu zmiany cen rynkowych.</i>"
            elements.append(Paragraph(validity_text, validity_style))
            
            # Zbuduj PDF
            doc.build(elements)
            return True
            
        except Exception as e:
            print(f"Błąd generowania PDF: {e}")
            return False
