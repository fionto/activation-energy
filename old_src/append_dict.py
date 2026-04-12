def append_point(collection, reading):
    """
    Appends values from a dictionary containing 'readings' to the 
    corresponding lists contained into the collection dictionary.
    """
    for k_r, v_r in reading.items():

        if k_r in collection:
            collection[k_r].append(v_r)

    # le funzioni che modificano oggetti in-place di norma restituiscono None. 
    # Il tuo return collection non è errato, ma rompi la convenzione di .append() 
    # e di librerie standard. Se vuoi chaining, va bene; altrimenti rimuovi il return.
    return collection


collection = {
    'voltage' : [],
    'current' : [],
    'std_dev' : [],
}

reading = {
    'voltage' : 10.0,
    'current' : 4.81472e-09,
    'std_dev' : 1.7902e-10,
}

print(append_point(collection, reading))