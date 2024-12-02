import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
from datetime import datetime, timedelta

# Conectar a la base de datos PostgreSQL
class ConexionDB:
    def __init__(self, dbname="inventario", user="postgres", password="1234", host="localhost", port="5432"):
        try:
            self.conn = psycopg2.connect(
                dbname=dbname, user=user, password=password, host=host, port=port
            )
            self.cur = self.conn.cursor()
            print("Conexión a la base de datos establecida")
        except Exception as e:
            print(f"Error al conectar a la base de datos: {e}")
            self.conn = None
            self.cur = None

    def close(self):
        if self.conn:
            self.conn.close()

# Función para obtener productos desde la base de datos (puede incluir búsqueda)
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

# Función para cargar productos en el treeview (con o sin filtro)
def cargar_productos(busqueda=""):
    for item in treeview_productos.get_children():
        treeview_productos.delete(item)
    productos = obtener_productos(busqueda)
    for producto in productos:
        treeview_productos.insert("", "end", values=producto)

# Función para buscar productos en tiempo real
def buscar_producto():
    busqueda = entry_buscar.get()
    cargar_productos(busqueda)

# Función para agregar producto al inventario
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

# Función para eliminar producto
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

# Función para actualizar producto
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

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Sistema de Control y Financiero de Inventarios")

# Conexión a la base de datos
db = ConexionDB()

# Sección de Inventario
frame_inventario = ttk.Frame(ventana)
frame_inventario.pack(fill="both", expand=True)

# Crear un treeview para los productos
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

# Cuadro de búsqueda
label_buscar = tk.Label(ventana, text="Buscar Producto:")
label_buscar.pack(pady=10)
entry_buscar = tk.Entry(ventana)
entry_buscar.pack(pady=5)
entry_buscar.bind("<KeyRelease>", lambda event: buscar_producto())  # Buscar al escribir

# Botones para CRUD
boton_agregar = tk.Button(ventana, text="Agregar Producto", command=agregar_producto)
boton_agregar.pack()

boton_eliminar = tk.Button(ventana, text="Eliminar Producto", command=eliminar_producto)
boton_eliminar.pack()

boton_actualizar = tk.Button(ventana, text="Actualizar Producto", command=actualizar_producto)
boton_actualizar.pack()

# Cargar productos al iniciar
cargar_productos()

# Función para mostrar balance general
def mostrar_balance():
    ventas, inventario = balance_general()
    messagebox.showinfo("Balance General", f"Total Ventas: ${ventas}\nValor Inventario: ${inventario}")

# Botón para mostrar balance general
boton_balance = tk.Button(ventana, text="Balance General", command=mostrar_balance)
boton_balance.pack()

ventana.mainloop()

# Cerrar la conexión a la base de datos al finalizar
if db.conn:
    db.close()
