# -*- coding: utf-8 -*-

from cod import cod_check, cod_search
from aiida.tools.dbimporters.plugins.cod import CodDbImporter
from aiida_related.group_initialize import Create_group

#from aiida.orm import Code, Computer, Data, Node, StructureData


def find_structure(response):
    """ 
    given the provided input, look for structure in database.
    different databases might be supported.
    for now, support the open database through aiida 
    """

    if response.ins.get('structure_type'):
        if response.ins["database"] in response.allowed['supported_database']:
            if response.ins['database'] == 'COD':
                # grep usable and unusable keywords for COD
                (used, unused) = cod_check(response.ins['query'])
                response.Structure_Add(
                    used_query_keywords=used, 
                    unrecognized_query_keywords=unused)
                # perform a database search according to the usable keywords
                cifs = cod_search(used)  # aiida database object
                n_structures = len(cifs)
                response.Structure_Add(
                    found_structures=n_structures
                )
                if n_structures == 0:
                    response.Set_Warning('No structure matches the query', 400)
                    return None
                else:
                    cod_info = []
                    if n_structures >= 2:
                        response.Set_Warning(
                            'Multiple matches to the query. Consider adding a more specific request, or choose one ID from the list. Returning the first structure. Proceed at your own risk!', 200)
                    for i in cifs:
                        cod_info.append(i.source)
                    response.Structure_Add(
                        cod_entries=cod_info
                    )
                    mystructure = cifs[0].get_aiida_structure()
                    mystructure.store()
                    samenodes = mystructure.get_all_same_nodes()
                    for k in samenodes:
                        print k.uuid
                    if len(mystructure.get_all_same_nodes()) != 0:
                        response.Set_Warning(
                            'Created structure id={} matches {} other structures'.format(
                                mystructure.id, len(samenodes)
                            ), 200
                        )
                    else:
                        mystructure.store()
                    response.Structure_Add(
                        aiida_id=mystructure.id,
                        aiida_uuid=mystructure.uuid
                    )
                    Ginestra_Group = Create_group(groupname='ginestra')
                    Ginestra_Group.add_nodes(mystructure)
                    response.Structure_Add(
                        mycif=mystructure.attributes
                    )
                

                
                




                
