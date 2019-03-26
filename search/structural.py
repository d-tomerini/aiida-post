# -*- coding: utf-8 -*-

from cod import cod_check, cod_search
def find_structure(response):
    """ 
    given the provided input, look for structure in database.
    different databases might be supported.
    for now, support the open database through aiida 
    """

    if response.instructure.get("structure_type"):
        if response.instructure["database"] in response.allowed["supported_database"]:
            if response.instructure["database"] == "COD":
                # grep usable and unusable keywords for COD
                (used, unused) = cod_check(response.instructure['query'])
                response.Structure_Add(
                    used_query_keywords=used, 
                    unrecognized_query_keywords=unused)
                # perform a database search according to the usable keywords
                cif_numbers = cod_search(used)
                n_structures = len(cif_numbers)
                response.Structure_Add(
                    found_structures=len(cif_numbers)
                )
                if n_structures == 0:
                    response.Set_Warning("No structure matches the query",200)
                else:
                    if n_structures >= 2:
                        response.Set_Warning("Multiple structure matches the query. Proceed at your own risk",200)
                        



                
