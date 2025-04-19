import os
from datetime import datetime
from typing import Dict, Any

def generate_invoice(sale: Dict[str, Any]) -> str:
    """Generate a text invoice for a sale"""
    # Create the invoices directory if it doesn't exist
    os.makedirs("invoices", exist_ok=True)
    
    # Define the invoice path
    invoice_path = os.path.join("invoices", f"invoice_{sale['id']}.txt")
    
    # ASCII art for the chicken and egg
    chicken_ascii = """\
 .==;=.
/ _ _ \\
| o o |
\\ /\\ /    ,
,/'-=\\/=-'\\,     |\\  /\\/  \\/|    ,_
/ /    \\ \\  ;   \\/ `';  , \\_',
| /      \\ |             \\   /  
\\/ \\  / \\/          '.  .' /`.
           '.  .'  `~~`  , /\\  ``
           _|`~~`|_     .  `
           /|\\   /|\\
"""

    egg_ascii = """\
      _______
    /         \\
   /           \\
  |             |
  |             |
   \\           /
    \\_________/
"""
    
    # Format the current date
    formatted_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Prepare the invoice content
    invoice_content = []
    invoice_content.append(chicken_ascii)
    invoice_content.append(" " * 30 + egg_ascii)
    invoice_content.append("\n" + "=" * 60)
    invoice_content.append("AVÍCOLA LLANO GRANDE SAS")
    invoice_content.append("NIT: 870545489-0")
    invoice_content.append("=" * 60)
    invoice_content.append("\n" + " " * 20 + "FACTURA DE VENTA" + " " * 20)
    invoice_content.append("=" * 60)
    invoice_content.append(f"Fecha: {formatted_date}")
    invoice_content.append(f"No. Factura: {sale['id']}")
    invoice_content.append("\nDatos del Cliente:")
    invoice_content.append(f"Nombre: {sale['customer_name']}")
    invoice_content.append(f"Documento: {sale['customer_document']}")
    invoice_content.append("\nDetalle de la compra:")
    invoice_content.append("-" * 60)
    invoice_content.append(f"{'Descripción':<20} {'Cantidad':<10} {'Precio Unit':<15} {'Total':<15}")
    invoice_content.append("-" * 60)
    
    # Add items to the invoice
    for item in sale['items']:
        unit_type = "cubeta (30)" if item['unit_type'] == "cubeta" else "docena (12)"
        description = f"{item['egg_type'].capitalize()} {item['egg_size']} {unit_type}"
        quantity = item['quantity']
        unit_price = item['unit_price']
        subtotal = item['subtotal']
        
        invoice_content.append(f"{description:<20} {quantity:<10} ${unit_price:<14.2f} ${subtotal:<14.2f}")
    
    invoice_content.append("-" * 60)
    invoice_content.append(f"{'Subtotal:':<46} ${sale['subtotal']:<12.2f}")
    invoice_content.append(f"{'IVA (5%):':<46} ${sale['iva']:<12.2f}")
    invoice_content.append(f"{'TOTAL:':<46} ${sale['total']:<12.2f}")
    invoice_content.append("=" * 60)
    invoice_content.append("\nGracias por su compra!")
    invoice_content.append("Avícola Llano Grande SAS")
    
    # Write the invoice to a file
    with open(invoice_path, "w", encoding="utf-8") as f:
        f.write("\n".join(invoice_content))
    
    return invoice_path