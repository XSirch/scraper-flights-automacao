from fast_flights import FlightData, Passengers, Result, get_flights_from_filter, get_flights, TFSData, create_filter
import tkinter as tk
from tkinter import ttk, messagebox

def search_flights(date: str, origem: str, destino: str) -> Result:
    """
    Busca voos com base na data, aeroporto de origem e aeroporto de destino.

    Parâmetros:
        date (str): Data do voo no formato YYYY-MM-DD.
        origem (str): Código do aeroporto de origem.
        destino (str): Código do aeroporto de destino.

    Retorna:
        Result: Resultado da busca de voos.
    """
    
    '''    result: Result = get_flights(
        flight_data=[
            FlightData(date=date, from_airport=origem, to_airport=destino)
        ],
        trip="one-way",
        seat="economy",
        passengers=Passengers(adults=1, children=0, infants_in_seat=0, infants_on_lap=0),
        fetch_mode="fallback",
    )'''
    filter: TFSData = create_filter(
        flight_data=[
            FlightData(
                date=date,
                from_airport=origem,
                to_airport=destino,
            )
        ],
        trip="one-way",
        passengers=Passengers(adults=1, children=0, infants_in_seat=0, infants_on_lap=0),
        seat="economy",
        max_stops=2,
    )
    filter.as_b64()  # Base64-encoded (bytes)
    filter.to_string()  # Serialize to string
    result = get_flights_from_filter(filter)
    

    return result




def create_gui():
    root = tk.Tk()
    root.title("Pesquisa de Voos")
    root.geometry("400x250")
    
    style = ttk.Style(root)
    style.theme_use("clam")
    
    frame = ttk.Frame(root, padding="10")
    frame.pack(fill=tk.BOTH, expand=True)
    
    # Campo Data
    lbl_date = ttk.Label(frame, text="Data (YYYY-MM-DD):")
    lbl_date.grid(row=0, column=0, sticky=tk.W, pady=5)
    entry_date = ttk.Entry(frame, width=30)
    entry_date.grid(row=0, column=1, pady=5)
    
    # Campo Origem
    lbl_origem = ttk.Label(frame, text="Origem (Aeroporto):")
    lbl_origem.grid(row=1, column=0, sticky=tk.W, pady=5)
    entry_origem = ttk.Entry(frame, width=30)
    entry_origem.grid(row=1, column=1, pady=5)
    
    # Campo Destino
    lbl_destino = ttk.Label(frame, text="Destino (Aeroporto):")
    lbl_destino.grid(row=2, column=0, sticky=tk.W, pady=5)
    entry_destino = ttk.Entry(frame, width=30)
    entry_destino.grid(row=2, column=1, pady=5)
    
    def on_search():
        date = entry_date.get().strip()
        origem = entry_origem.get().strip()
        destino = entry_destino.get().strip()
        
        if not date or not origem or not destino:
            messagebox.showerror("Erro", "Preencha todos os campos.")
            return
        
        try:
            result = search_flights(date, origem, destino)
            result_text = str(result)
            messagebox.showinfo("Resultado", result_text)
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {e}")
    
    btn_search = ttk.Button(frame, text="Buscar Voos", command=on_search)
    btn_search.grid(row=3, column=0, columnspan=2, pady=20)
    
    root.mainloop()

if __name__ == "__main__":
    create_gui()
