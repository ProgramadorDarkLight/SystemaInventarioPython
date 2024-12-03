import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
from datetime import datetime, timedelta

# Conectar a la base de datos PostgreSQL
class ConexionDB:
    def __init__(self, dbname="inventario", user="postgres", password="1234", host="localhost", port="5432"):
        try:
            self.conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
            self.cur = self.conn.cursor()
            print("Conexión a la base de datos establecida")
        except Exception as e:
            print(f"Error al conectar a la base de datos. Excepción:{e}")
            self.conn = None
            self.cur = None

    def close(self):
        if self.conn:
            self.conn.close()

# Funciones para interactuar con la base de datos

def obtener_productos(busqueda=""):
    if db.cur:
        try:
            query = "SELECT id, nombre, descripcion, precio, stock FROM productos"
            if busqueda:
                query += " WHERE nombre ILIKE %s"
                db.cur.execute(query, ('%' + busqueda + '%',))
            else:
                db.cur.execute(query)
            return db.cur.fetchall()
        except Exception as e:
            print(f"Error al obtener productos: {e}")
            return []
    else:
        print("Conexión no establecida, no se pueden obtener productos")
        return []

def cargar_productos(busqueda=""):
    for item in treeview_productos.get_children():
        treeview_productos.delete(item)
    productos = obtener_productos(busqueda)
    for producto in productos:
        treeview_productos.insert("", "end", values=producto)

def buscar_producto():
    busqueda = entry_buscar.get()
    cargar_productos(busqueda)

def agregar_producto():
    def guardar_producto():
        nombre = entry_nombre.get()
        descripcion = entry_descripcion.get()
        precio = float(entry_precio.get())
        stock = int(entry_stock.get())

        try:
            db.cur.execute("INSERT INTO productos (nombre, descripcion, precio, stock) VALUES (%s, %s, %s, %s)",
                           (nombre, descripcion, precio, stock))
            db.conn.commit()
            messagebox.showinfo("Información", "Producto agregado exitosamente")
            cargar_productos()
            ventana_agregar.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar el producto: {e}")

    ventana_agregar = tk.Toplevel(ventana)
    ventana_agregar.title("Agregar Producto")

    label_nombre = tk.Label(ventana_agregar, text="Nombre")
    label_nombre.pack()
    entry_nombre = tk.Entry(ventana_agregar)
    entry_nombre.pack()

    label_descripcion = tk.Label(ventana_agregar, text="Descripción")
    label_descripcion.pack()
    entry_descripcion = tk.Entry(ventana_agregar)
    entry_descripcion.pack()

    label_precio = tk.Label(ventana_agregar, text="Precio")
    label_precio.pack()
    entry_precio = tk.Entry(ventana_agregar)
    entry_precio.pack()

    label_stock = tk.Label(ventana_agregar, text="Stock")
    label_stock.pack()
    entry_stock = tk.Entry(ventana_agregar)
    entry_stock.pack()

    boton_guardar = tk.Button(ventana_agregar, text="Guardar", command=guardar_producto)
    boton_guardar.pack()

def eliminar_producto():
    try:
        selected_item = treeview_productos.selection()[0]
        producto_id = treeview_productos.item(selected_item)['values'][0]
        db.cur.execute("DELETE FROM productos WHERE id = %s", (producto_id,))
        db.conn.commit()
        messagebox.showinfo("Información", "Producto eliminado exitosamente")
        cargar_productos()
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo eliminar el producto: {e}")

def actualizar_producto():
    try:
        selected_item = treeview_productos.selection()[0]
        producto_id = treeview_productos.item(selected_item)['values'][0]

        def guardar_cambios():
            nombre = entry_nombre.get()
            descripcion = entry_descripcion.get()
            precio = entry_precio.get()
            stock = entry_stock.get()
            try:
                db.cur.execute("UPDATE productos SET nombre = %s, descripcion = %s, precio = %s, stock = %s WHERE id = %s",
                               (nombre, descripcion, precio, stock, producto_id))
                db.conn.commit()
                messagebox.showinfo("Información", "Producto actualizado exitosamente")
                cargar_productos()
                ventana_actualizar.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar el producto: {e}")

        ventana_actualizar = tk.Toplevel(ventana)
        ventana_actualizar.title("Actualizar Producto")

        label_nombre = tk.Label(ventana_actualizar, text="Nombre")
        label_nombre.pack()
        entry_nombre = tk.Entry(ventana_actualizar)
        entry_nombre.pack()
        entry_nombre.insert(0, treeview_productos.item(selected_item)['values'][1])

        label_descripcion = tk.Label(ventana_actualizar, text="Descripción")
        label_descripcion.pack()
        entry_descripcion = tk.Entry(ventana_actualizar)
        entry_descripcion.pack()
        entry_descripcion.insert(0, treeview_productos.item(selected_item)['values'][2])

        label_precio = tk.Label(ventana_actualizar, text="Precio")
        label_precio.pack()
        entry_precio = tk.Entry(ventana_actualizar)
        entry_precio.pack()
        entry_precio.insert(0, treeview_productos.item(selected_item)['values'][3])

        label_stock = tk.Label(ventana_actualizar, text="Stock")
        label_stock.pack()
        entry_stock = tk.Entry(ventana_actualizar)
        entry_stock.pack()
        entry_stock.insert(0, treeview_productos.item(selected_item)['values'][4])

        boton_guardar = tk.Button(ventana_actualizar, text="Guardar Cambios", command=guardar_cambios)
        boton_guardar.pack()
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar el producto para actualizar: {e}")

# Funciones de compra y venta

def comprar_producto():
    def procesar_compra():
        producto_id = entry_producto_id.get()
        cantidad = int(entry_cantidad.get())
        proveedor = entry_proveedor.get()
        fecha = datetime.now().strftime('%Y-%m-%d')

        try:
            db.cur.execute("SELECT stock FROM productos WHERE id = %s", (producto_id,))
            producto = db.cur.fetchone()

            if producto:
                nuevo_stock = producto[0] + cantidad
                db.cur.execute("UPDATE productos SET stock = %s WHERE id = %s", (nuevo_stock, producto_id))
                db.cur.execute("INSERT INTO compras (producto_id, cantidad, proveedor, fecha) VALUES (%s, %s, %s, %s)",
                               (producto_id, cantidad, proveedor, fecha))
                db.conn.commit()

                messagebox.showinfo("Compra exitosa", f"Se ha comprado {cantidad} unidades.")
                ventana_compra.destroy()
                cargar_productos()
            else:
                messagebox.showerror("Error", "Producto no encontrado en inventario.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo realizar la compra: {e}")

    ventana_compra = tk.Toplevel(ventana)
    ventana_compra.title("Compra de Producto")

    label_producto_id = tk.Label(ventana_compra, text="ID Producto")
    label_producto_id.pack()
    entry_producto_id = tk.Entry(ventana_compra)
    entry_producto_id.pack()

    label_cantidad = tk.Label(ventana_compra, text="Cantidad")
    label_cantidad.pack()
    entry_cantidad = tk.Entry(ventana_compra)
    entry_cantidad.pack()

    label_proveedor = tk.Label(ventana_compra, text="Proveedor")
    label_proveedor.pack()
    entry_proveedor = tk.Entry(ventana_compra)
    entry_proveedor.pack()

    boton_procesar = tk.Button(ventana_compra, text="Procesar Compra", command=procesar_compra)
    boton_procesar.pack()

def vender_producto():
    def procesar_venta():
        producto_id = entry_producto_id.get()
        cantidad = int(entry_cantidad.get())
        cliente = entry_cliente.get()
        fecha = datetime.now().strftime('%Y-%m-%d')

        try:
            db.cur.execute("SELECT stock, precio FROM productos WHERE id = %s", (producto_id,))
            producto = db.cur.fetchone()

            if producto and producto[0] >= cantidad:
                nuevo_stock = producto[0] - cantidad
                db.cur.execute("UPDATE productos SET stock = %s WHERE id = %s", (nuevo_stock, producto_id))
                db.cur.execute("INSERT INTO ventas (producto_id, cantidad, cliente, fecha, total) VALUES (%s, %s, %s, %s, %s)",
                               (producto_id, cantidad, cliente, fecha, cantidad * producto[1]))
                db.conn.commit()

                messagebox.showinfo("Venta exitosa", f"Se ha vendido {cantidad} unidades.")
                ventana_venta.destroy()
                cargar_productos()
            else:
                messagebox.showerror("Error", "No hay suficiente stock para realizar la venta.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo realizar la venta: {e}")

    ventana_venta = tk.Toplevel(ventana)
    ventana_venta.title("Venta de Producto")

    label_producto_id = tk.Label(ventana_venta, text="ID Producto")
    label_producto_id.pack()
    entry_producto_id = tk.Entry(ventana_venta)
    entry_producto_id.pack()

    label_cantidad = tk.Label(ventana_venta, text="Cantidad")
    label_cantidad.pack()
    entry_cantidad = tk.Entry(ventana_venta)
    entry_cantidad.pack()

    label_cliente = tk.Label(ventana_venta, text="Cliente")
    label_cliente.pack()
    entry_cliente = tk.Entry(ventana_venta)
    entry_cliente.pack()

    boton_procesar = tk.Button(ventana_venta, text="Procesar Venta", command=procesar_venta)
    boton_procesar.pack()

# Función para mostrar balance general
def mostrar_balance():
    ventas, inventario = balance_general()
    messagebox.showinfo("Balance General", f"Total Ventas: ${ventas}\nValor Inventario: ${inventario}")

# Función de balance general
def balance_general():
    try:
        db.cur.execute("SELECT SUM(total) FROM ventas")
        ventas = db.cur.fetchone()[0] or 0.0
        db.cur.execute("SELECT SUM(precio * stock) FROM productos")
        inventario = db.cur.fetchone()[0] or 0.0
        return ventas, inventario
    except Exception as e:
        print(f"Error al obtener balance: {e}")
        return 0.0, 0.0

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Sistema de Control y Financiero de Inventarios")

# Conexión a la base de datos
db = ConexionDB()

# Crear la interfaz de inventario
frame_inventario = ttk.Frame(ventana)
frame_inventario.pack(fill="both", expand=True)

treeview_productos = ttk.Treeview(frame_inventario, columns=("id", "nombre", "descripcion", "precio", "stock"), show="headings")
treeview_productos.column("#0", width=0, stretch=tk.NO)
treeview_productos.column("id", anchor=tk.W, width=50)
treeview_productos.column("nombre", anchor=tk.W, width=200)
treeview_productos.column("descripcion", anchor=tk.W, width=300)
treeview_productos.column("precio", anchor=tk.W, width=100)
treeview_productos.column("stock", anchor=tk.W, width=100)

treeview_productos.heading("id", text="ID")
treeview_productos.heading("nombre", text="Nombre")
treeview_productos.heading("descripcion", text="Descripción")
treeview_productos.heading("precio", text="Precio")
treeview_productos.heading("stock", text="Stock")

treeview_productos.pack()

label_buscar = tk.Label(ventana, text="Buscar Producto:")
label_buscar.pack(pady=10)
entry_buscar = tk.Entry(ventana)
entry_buscar.pack(pady=5)
entry_buscar.bind("<KeyRelease>", lambda event: buscar_producto())

# Botones CRUD y transacciones
boton_agregar = tk.Button(ventana, text="Agregar Producto", command=agregar_producto)
boton_agregar.pack()

boton_eliminar = tk.Button(ventana, text="Eliminar Producto", command=eliminar_producto)
boton_eliminar.pack()

boton_actualizar = tk.Button(ventana, text="Actualizar Producto", command=actualizar_producto)
boton_actualizar.pack()

# Botones de compra y venta
boton_comprar = tk.Button(ventana, text="Comprar Producto", command=comprar_producto)
boton_comprar.pack()

boton_vender = tk.Button(ventana, text="Vender Producto", command=vender_producto)
boton_vender.pack()

boton_balance = tk.Button(ventana, text="Balance General", command=mostrar_balance)
boton_balance.pack()

cargar_productos()

ventana.mainloop()

# Cerrar conexión
if db.conn:
    db.close()
