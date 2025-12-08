from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
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
        
        # Dodaj niestandardowe style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='CategoryHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c5aa0'),
            spaceAfter=10,
            spaceBefore=20,
            leftIndent=0
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
                    ['Nazwa', 'Ilość', 'J.m.', 'Cena netto\njedn.', 'VAT', 'Cena brutto\njedn.', 'Wartość\nnetto', 'Wartość\nbrutto']
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
                    
                    table_data.append([
                        item['name'],
                        f"{item['quantity']:.2f}",
                        item.get('unit', 'szt.'),
                        f"{prices['net_unit']:.2f} zł",
                        f"{item['vat_rate']:.0f}%",
                        f"{prices['gross_unit']:.2f} zł",
                        f"{prices['net_total']:.2f} zł",
                        f"{prices['gross_total']:.2f} zł"
                    ])
                
                # Podsuma kategorii
                table_data.append([
                    f'Suma {category_name}', '', '', '', '', '',
                    f"{category_total_net:.2f} zł",
                    f"{category_total_gross:.2f} zł"
                ])
                
                grand_total_net += category_total_net
                grand_total_gross += category_total_gross
                
                # Stwórz tabelę
                table = Table(table_data, colWidths=[6*cm, 1.5*cm, 1*cm, 2*cm, 1.2*cm, 2*cm, 2*cm, 2*cm])
                
                # Stylizacja tabeli
                table.setStyle(TableStyle([
                    # Nagłówek
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    
                    # Dane
                    ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -2), 8),
                    ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                    ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    
                    # Siatka
                    ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
                    ('LINEBELOW', (0, -1), (-1, -1), 1, colors.HexColor('#2c5aa0')),
                    
                    # Podsuma kategorii
                    ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e6f2ff')),
                    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, -1), (-1, -1), 9),
                    
                    # Padding
                    ('TOPPADDING', (0, 1), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ]))
                
                elements.append(table)
                elements.append(Spacer(1, 15))
            
            # Suma końcowa
            elements.append(Spacer(1, 10))
            summary_data = [
                ['SUMA CAŁKOWITA NETTO:', f"{grand_total_net:.2f} zł"],
                ['SUMA CAŁKOWITA BRUTTO:', f"{grand_total_gross:.2f} zł"]
            ]
            
            summary_table = Table(summary_data, colWidths=[14*cm, 4*cm])
            summary_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1a5490')),
                ('LINEABOVE', (0, 0), (-1, 0), 2, colors.HexColor('#2c5aa0')),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
            ]))
            
            elements.append(summary_table)
            
            # Zbuduj PDF
            doc.build(elements)
            return True
            
        except Exception as e:
            print(f"Błąd generowania PDF: {e}")
            return False
