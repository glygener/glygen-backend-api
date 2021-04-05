var frontendObj = {
        "sunb_bio_molecules": {
                "name": "BioMolecules",
                "children": [
                        {
                                "organism": {
                                        "organism_list": [
                                                {
                                                        "id": 9606,
                                                        "name": "Homo sapiens"
                                                }
                                        ],
                                        "operation":"or"
                                },
                                "name": "Human Glycans",
                                "children": [
                                        {
                                                "organism": {
                                                        "organism_list": [
                                                                {
                                                                        "id": 9606,
                                                                        "name": "Homo sapiens"
                                                                }
                                                        ],
                                                        "operation":"or"
                                                },
                                                "glycan_type": "N-Glycan",
                                                "name": "N-Glycan",
                                                "size": 1605
                                        },
                                        {
                                                "organism": {
                                                        "organism_list": [
                                                                {
                                                                        "id": 9606,
                                                                        "name": "Homo sapiens"
                                                                }
                                                        ],
                                                        "operation":"or"
                                                },
                                                "glycan_type": "O-Glycan",
                                                "name": "O-Glycan",
                                                "size": 353
                                        },
                                        {
                                                "organism": {
                                                        "organism_list": [
                                                                {
                                                                        "id": 9606,
                                                                        "name": "Homo sapiens"
                                                                }
                                                        ],
                                                        "operation":"or"
                                                },
                                                "glycan_type": "Other",
                                                "name": "Other",
                                                "size": 2088
                                        }
                                ]
                        },
                        {
                                "organism": {
                                        "id": 9606,
                                        "name": "Homo sapiens"
                                },
                                "name": "Human Proteins",
                                "size": 20950,
                                "children": [{
                                        "name": "",
                                        "size": 0
                                        }       
                                ]
                        },
                        {
                                "organism": {
                                        "organism_list": [
                                                {
                                                        "id": 10090,
                                                        "name": "Mus musculus"
                                                }
                                        ],
                                        "operation":"or"                
                                },
                                "name": "Mouse Glycans",
                                "children": [{
                                                "organism": {
                                                        "organism_list": [
                                                                {
                                                                        "id": 10090,
                                                                        "name": "Mus musculus"
                                                                }
                                                        ],
                                                        "operation":"or"                
                                                },
                                                "glycan_type": "N-Glycan",
                                                "name": "N-Glycan",
                                                "size": 357
                                        },
                                        {
                                                "organism": {
                                                        "organism_list": [
                                                                {
                                                                        "id": 10090,
                                                                        "name": "Mus musculus"
                                                                }
                                                        ],
                                                        "operation":"or"                
                                                },
                                                "glycan_type": "O-Glycan",
                                                "name": "O-Glycan",
                                                "size": 25
                                        },
                                        {
                                                "organism": {
                                                        "organism_list": [
                                                                {
                                                                        "id": 10090,
                                                                        "name": "Mus musculus"
                                                                }
                                                        ],
                                                        "operation":"or"                
                                                },
                                                "glycan_type": "Other",
                                                "name": "Other",
                                                "size": 259
                                        }
                                ]
                        },
                        {
                                "organism": {
                                        "id": 10090,
                                        "name": "Mus musculus"
                                },
                                "name": "Mouse Proteins",
                                "size": 22282,
                                "children": [{
                                        "name": "",
                                        "size": 0
                                        }       
                                ]
                        },
                        {
                                "organism": {
                                        "organism_list": [
                                                {
                                                        "id": 10116,
                                                        "name": "Rattus norvegicus"
                                                }
                                        ],
                                        "operation":"or"                
                                },
                                "name": "Rat Glycans",
                                "children": [{
                                                "organism": {
                                                        "organism_list": [
                                                                {
                                                                        "id": 10116,
                                                                        "name": "Rattus norvegicus"
                                                                }
                                                        ],
                                                        "operation":"or"                
                                                },
                                                "glycan_type": "N-Glycan",
                                                "name": "N-Glycan",
                                                "size": 2502
                                        },
                                        {
                                                "organism": {
                                                        "organism_list": [
                                                                {
                                                                        "id": 10116,
                                                                        "name": "Rattus norvegicus"
                                                                }
                                                        ],
                                                        "operation":"or"                
                                                },
                                                "glycan_type": "O-Glycan",
                                                "name": "O-Glycan",
                                                "size": 800
                                        },
                                        {
                                                "organism": {
                                                        "organism_list": [
                                                                {
                                                                        "id": 10116,
                                                                        "name": "Rattus norvegicus"
                                                                }
                                                        ],
                                                        "operation":"or"                
                                                },
                                                "glycan_type": "Other",
                                                "name": "Other",
                                                "size": 49
                                        }
                                ]
                        },
                        {
                                "organism": {
                                        "id": 10116,
                                        "name": "Rattus norvegicus"
                                },
                                "name": "Rat Proteins",
                                "size": 21673,
                                "children": [{
                                        "name": "",
                                        "size": 0
                                        }       
                                ]
                        }
                ]
        },
        "venn_glycan_species": [
                {
                        "sets": [0],
                        "tooltipname": "Human glycans",
                        "organism": {
                                "organism_list": [
                                        {
                                                "id": 9606,
                                                "name": "Homo sapiens"
                                        }
                                ],
                                "operation":"or"
                        },
                        "name": "Human glycans",
                        "size": 4046
                },
                {
                        "sets": [1],
                        "tooltipname": "Mouse glycans",
                        "organism": {
                                "organism_list": [
                                        {
                                                "id": 10090,
                                                "name": "Mus musculus"
                                        }
                                ],
                                "operation":"or"                
                        },
                        "name": "Mouse glycans",
                        "size": 641
                },
                {
                        "sets": [2],
                        "tooltipname": "Rat glycans",
                        "organism": {
                                "organism_list": [
                                        {
                                                "id": 10116,
                                                "name": "Rattus norvegicus"
                                        }
                                ],
                                "operation":"or"                
                        },
                        "name": "Rat glycans",
                        "size": 250
                },
                {
                        "sets": [0, 1],
                        "tooltipname": "Human & Mouse glycans",
                        "organism": {
                                "organism_list": [
                                        {
                                                "id": 9606,
                                                "name": "Homo sapiens"
                                        },
                                        {
                                                "id": 10090,
                                                "name": "Mus musculus"
                                        }
                                ],
                                "operation":"and"
                        },
                        "name": "",
                        "size": 4378
                },
                {
                        "sets": [0, 2],
                        "tooltipname": "Human & Rat glycans",
                        "organism": {
                                "organism_list": [
                                        {
                                                "id": 9606,
                                                "name": "Homo sapiens"
                                        },
                                        {
                                                "id": 10116,
                                                "name": "Rattus norvegicus"
                                        }
                                ],
                                "operation":"and"
                        },
                        "name": "",
                        "size": 4183
                },
                {
                        "sets": [1, 2],
                        "tooltipname": "Mouse & Rat glycans",
                        "organism": {
                                "organism_list": [
                                        {
                                                "id": 10090,
                                                "name": "Mus musculus"
                                        },
                                        {
                                                "id": 10116,
                                                "name": "Rattus norvegicus"
                                        }
                                ],
                                "operation":"and"
                        },
                        "name": "",
                        "size": 841
                },
                {
                        "sets": [0, 1, 2],
                        "tooltipname": "Human & Mouse & Rat glycans",
                        "organism": {
                                "organism_list": [
                                        {
                                                "id": 9606,
                                                "name": "Homo sapiens"
                                        },
                                        {
                                                "id": 10090,
                                                "name": "Mus musculus"
                                        },
                                        {
                                                "id": 10116,
                                                "name": "Rattus norvegicus"
                                        }
                                ],
                                "operation":"and"
                        },
                        "name": "",
                        "size": 4507
                }
        ],
        "sunb_glycan_type_subtype": {
        "name":"",
        "children":[
                {
                "name": "N-glycan",
                "children": [
                                   {
                                          "name": "Hybrid",
                                          "size": 85
                                   },
                                   {
                                          "name":"Complex",
                                          "size": 1796
                                   },
                                        {
                                                "name": "High mannose",
                                                "size": 78
                                        },
                                        {
                                                "name": "Other",
                                                "size": 606
                                        }
                                ]
                },
                {
                                "name":"O-glycan",
                                "children":[
                                        {
                                "name": "Core 1",
                                "size": 100
                        },
                        {
                                "name": "Core 2",
                                                "size": 189
                        },
                        {
                                "name": "Core 3",
                                                "size": 53
                        },
                                        {
                                                "name": "Core 4",
                                                "size": 38
                                        },
                                        {
                                                "name": "Core 5",
                                                "size": 5
                                        },
                                        {
                                                "name": "Core 6",
                                                "size": 8
                                        },
                                        {
                                                "name": "Core 7",
                                                "size": 1
                                        }
                                ]
                }
        ]
        },
        "sunb_glycan_organism_type": {  
                "name": "",
                "children": [
                        {
                                "organism": {
                                        "organism_list": [
                                                {
                                                        "id": 9606,
                                                        "name": "Homo sapiens"
                                                }
                                        ],
                                        "operation":"or"
                                },
                                "name": "Human Glycans",
                                "children": [{
                                                "organism": {
                                                        "organism_list": [
                                                                {
                                                                        "id": 9606,
                                                                        "name": "Homo sapiens"
                                                                }
                                                        ],
                                                        "operation":"or"
                                                },
                                                "glycan_type": "N-Glycan",
                                                "name": "Human N-Glycans",
                                                "size": 989
                                        },
                                        {
                                                "organism": {
                                                        "organism_list": [
                                                                {
                                                                        "id": 9606,
                                                                        "name": "Homo sapiens"
                                                                }
                                                        ],
                                                        "operation":"or"
                                                },
                                                "glycan_type": "O-Glycan",
                                                "name": "Human O-Glycans",
                                                "size": 312
                                        },
                                        {
                                                "organism": {
                                                        "organism_list": [
                                                                {
                                                                        "id": 9606,
                                                                        "name": "Homo sapiens"
                                                                }
                                                        ],
                                                        "operation":"or"
                                                },
                                                "glycan_type": "Other",
                                                "name": "Human Other",
                                                "size": 2001
                                        }
                                ]
                        },
                        {
                                "organism": {
                                        "organism_list": [
                                                {
                                                        "id": 10090,
                                                        "name": "Mus musculus"
                                                }
                                        ],
                                        "operation":"or"
                                },
                                "name": "Mouse Glycans",
                                "children": [{
                                                "organism": {
                                                        "organism_list": [
                                                                {
                                                                        "id": 10090,
                                                                        "name": "Mus musculus"
                                                                }
                                                        ],
                                                        "operation":"or"
                                                },
                                                "glycan_type": "N-Glycan",
                                                "name": "Mouse N-Glycans",
                                                "size": 261
                                        },
                                        {
                                                "organism": {
                                                        "organism_list": [
                                                                {
                                                                        "id": 10090,
                                                                        "name": "Mus musculus"
                                                                }
                                                        ],
                                                        "operation":"or"
                                                },
                                                "glycan_type": "O-Glycan",
                                                "name": "Mouse O-Glycans",
                                                "size": 12
                                        },
                                        {
                                                "organism": {
                                                        "organism_list": [
                                                                {
                                                                        "id": 10090,
                                                                        "name": "Mus musculus"
                                                                }
                                                        ],
                                                        "operation":"or"
                                                },
                                                "glycan_type": "Other",
                                                "name": "Mouse Other",
                                                "size": 244
                                        }
                                ]
                        },
                        {
                                "organism": {
                                        "organism_list": [
                                                {
                                                        "id": 10116,
                                                        "name": "Rattus norvegicus"
                                                }
                                        ],
                                        "operation":"or"
                                },
                                "name": "Rat Glycans",
                                "children": [{
                                                "organism": {
                                                        "organism_list": [
                                                                {
                                                                        "id": 10116,
                                                                        "name": "Rattus norvegicus"
                                                                }
                                                        ],
                                                        "operation":"or"
                                                },
                                                "glycan_type": "N-Glycan",
                                                "name": "Rat N-Glycans",
                                                "size": 312
                                        },
                                        {
                                                "organism": {
                                                        "organism_list": [
                                                                {
                                                                        "id": 10116,
                                                                        "name": "Rattus norvegicus"
                                                                }
                                                        ],
                                                        "operation":"or"
                                                },
                                                "glycan_type": "O-Glycan",
                                                "name": "Rat O-Glycans",
                                                "size": 23
                                        },
                                        {
                                                "organism": {
                                                        "organism_list": [
                                                                {
                                                                        "id": 10116,
                                                                        "name": "Rattus norvegicus"
                                                                }
                                                        ],
                                                        "operation":"or"
                                                },
                                                "glycan_type": "Other",
                                                "name": "Rat Other",
                                                "size": 325
                                        }
                                ]
                        }
                ]
        },
        "donut_motif": [
                {
                        "name": "Lactosamine motif",
                        "size": 14389
                },
                {
                        "name": "N-Glycan core basic",
                        "size": 12326
                },
                {
                        "name": "N-Glycan complex",
                        "size": 8365
                },
                {
                        "name": "VIM",
                        "size": 3760
                },
                {
                        "name": "Lewis X",
                        "size": 3760
                },
                {
                        "name": "Blood group H",
                        "size": 2965
                },
                {
                        "name": "Neo Lactosamine",
                        "size": 2275
                },
                {
                        "name": "Polylactosamine",
                        "size": 2251
                },
                {
                        "name": "Galalpha1-3Gal epitope",
                        "size": 2088
                },
                {
                        "name": "O-Glycan core 1 fuzzy",
                        "size": 2028
                },
                {
                        "name": "LacDiNAc",
                        "size": 1323
                },
                {
                        "name": "O-Glycan core 6 Fuzzy",
                        "size": 1202
                },
                {
                        "name": "Sialyl Lewis X",
                        "size": 1103
                },
                {
                        "name": "N-Glycan high mannose",
                        "size": 1100
                },
                {
                        "name": "O-Glycan core 2 fuzzy",
                        "size": 928
                },
                {
                        "name": "O-Glycan core 1",
                        "size": 804
                },
                {
                        "name": "N-Glycan hybrid",
                        "size": 677
                },
                {
                        "name": "Blood group A",
                        "size": 578
                },
                {
                        "name": "Glycosphingolipid Neo-lacto series",
                        "size": 533
                },
                {
                        "name": "Lewis Y",
                        "size": 526
                },
                {
                        "name": "Lewis A",
                        "size": 502
                },
                {
                        "name": "O-Glycan core 3 fuzzy",
                        "size": 495
                },
                {
                        "name": "O-Glycan core 6",
                        "size": 470
                },
                {
                        "name": "O-Glycan core 2",
                        "size": 367
                },
                {
                        "name": "Glycosphingolipid Lacto series",
                        "size": 298
                },
                {
                        "name": "Blood group B",
                        "size": 212
                },
                {
                        "name": "O-Glycan core 3",
                        "size": 205
                },
                {
                        "name": "Glycosphingolipid Ganglio series",
                        "size": 194
                },
                {
                        "name": "N-Glycan truncated motif. First GlcpNAC cut off",
                        "size": 169
                },
                {
                        "name": "O-Glycan core 4 fuzzy",
                        "size": 168
                },
                {
                        "name": "Lewis B",
                        "size": 164
                },
                {
                        "name": "Pk-Antigen",
                        "size": 160
                },
                {
                        "name": "Lewis C",
                        "size": 103
                },
                {
                        "name": "Beta-glucan",
                        "size": 99
                },
                {
                        "name": "Sialyl Lewis A",
                        "size": 96
                },
                {
                        "name": "O-Glycan core 5 fuzzy",
                        "size": 84
                },
                {
                        "name": "Keratansulfate",
                        "size": 75
                },
                {
                        "name": "Hyluronan",
                        "size": 68
                },
                {
                        "name": "Glycosphingolipid Mollu series",
                        "size": 67
                },
                {
                        "name": "O-Glycan core 4",
                        "size": 65
                },
                {
                        "name": "P-Antigen",
                        "size": 50
                },
                {
                        "name": "Glycosphingolipid Gala series",
                        "size": 33
                },
                {
                        "name": "Cellulose like Glc(1-4)n",
                        "size": 33
                },
                {
                        "name": "Glycosphingolipid Arthro series",
                        "size": 24
                },
                {
                        "name": "O-Glycan core 5",
                        "size": 24
                },
                {
                        "name": "Chondroitin 4S",
                        "size": 24
                },
                {
                        "name": "GPI anchor core",
                        "size": 19
                },
                {
                        "name": "Glycosphingolipid Isoglobo series",
                        "size": 16
                },
                {
                        "name": "Lewis D",
                        "size": 16
                },
                {
                        "name": "Glycosphingolipid Globo series",
                        "size": 7
                },
                {
                        "name": "SDA",
                        "size": 7
                },
                {
                        "name": "Glycosphingolipid Muco series",
                        "size": 6
                },
                {
                        "name": "O-Glycan core 7 fuzzy",
                        "size": 6
                },
                {
                        "name": "O-Glycan core 7",
                        "size": 2
                },
                {
                        "name": "Heparin",
                        "size": 2
                },
                {
                        "name": "Peptidoglycan",
                        "size": 1
                },
                {
                        "name": "LPS core",
                        "size": 1
                },
                {
                        "name": "P1-Antigen",
                        "size": 1
                },
                {
                        "name": "Forssmann",
                        "size": 1
                },
                {
                        "name": "CAD",
                        "size": 1
                },
                {
                        "name": "Dermatansulfate",
                        "size": 1
                }
        ],
        "bar_mass_ranges": {
                "stepsize": 50,
                "data": [0, 0, 0, 6, 7, 7, 29, 44, 35, 42, 98, 51, 34, 80, 109, 44, 53, 110, 66, 92, 120, 144, 104, 91, 153, 135, 99, 179, 134, 116, 93, 166, 103, 95, 162, 127, 114, 135, 160, 117, 185, 156, 90, 179, 145, 143, 48, 136, 85, 43, 95, 110, 29, 52, 96, 20, 22, 181, 14, 35, 146, 29, 24, 25, 48, 4, 20, 26, 8, 11, 89, 1, 4, 105, 14, 13, 8, 2, 0, 1, 7, 5, 7, 2, 0, 3, 1, 0, 5, 3, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 2, 0, 0, 2]
        },
        "bar_sugar_ranges": {
                "stepsize": 1,
                "data": [17, 173, 401, 526, 589, 740, 852, 905, 943, 969, 1059, 1130, 920, 690, 660, 415, 256, 317, 201, 52, 34, 24, 10, 5, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 6]
        },
        "sunb_canon_isof_prot": {       
                "name": "",
                "children": [{
                                "organism": {
                                        "id": 9606,
                                        "name": "Homo sapiens"
                                },
                                "name": "Human Proteins",
                                "children": [{
                                                "organism": {
                                                        "id": 9606,
                                                        "name": "Homo sapiens"
                                                },
                                                "name": "Human Canonical",
                                                "size": 20950
                                        },
                                        {
                                                "organism": {
                                                        "id": 9606,
                                                        "name": "Homo sapiens"
                                                },
                                                "name": "Human Isoforms",
                                                "size": 73583
                                        }
                                ]
                        },
                        {
                                "organism": {
                                        "id": 10090,
                                        "name": "Mus musculus"
                                },
                                "name": "Mouse Proteins",
                                "children": [{
                                                "organism": {
                                                        "id": 10090,
                                                        "name": "Mus musculus"
                                                },
                                                "name": "Mouse Canonical",
                                                "size": 22282
                                        },
                                        {
                                                "organism": {
                                                        "id": 10090,
                                                        "name": "Mus musculus"
                                                },
                                                "name": "Mouse Isoforms",
                                                "size": 40870
                                        }
                                ]
                        },
                        {
                                "organism": {
                                        "id": 10116,
                                        "name": "Rattus norvegicus"
                                },
                                "name": "Rat Proteins",
                                "children": [{
                                                "organism": {
                                                        "id": 10116,
                                                        "name": "Rattus norvegicus"
                                                },
                                                "name": "Rat Canonical",
                                                "size": 21673
                                        },
                                        {
                                                "organism": {
                                                        "id": 10116,
                                                        "name": "Rattus norvegicus"
                                                },
                                                "name": "Rat Isoforms",
                                                "size": 9867
                                        }
                                ]
                        }
                ]
        },
        "venn_protein_homo": [
                {
                        "sets": [0],
                        "tooltipname": "Proteins",
                        "name": "Proteins",
                        "size": 20950,
                        "organism": {
                                "id": 9606,
                                "name": "Homo sapiens"
                        }
                },
                {
                        "sets": [1],
                        "tooltipname": "Enzymes",
                        "name": "Enzymes",
                        "size": 6000,
                        "organism": {
                                "id": 9606,
                                "name": "Homo sapiens"
                        }
                },
                {
                        "sets": [2],
                        "tooltipname": "Glycoproteins",
                        "name": "Glycoproteins",
                        "size": 4715,
                        "organism": {
                                "id": 9606,
                                "name": "Homo sapiens"
                        }
                },
                {
                        "sets": [0, 1],
                        "tooltipname": "Enzymes",
                        "name": "",
                        "size": 6000,
                        "organism": {
                                "id": 9606,
                                "name": "Homo sapiens"
                        }
                },
                {
                        "sets": [0, 2],
                        "tooltipname": "Glycoproteins",
                        "name": "",
                        "size": 4715,
                        "organism": {
                                "id": 9606,
                                "name": "Homo sapiens"
                        }
                },
                {
                        "sets": [0, 1, 2],
                        "tooltipname": "Glycoproteins & Enzymes",
                        "name": "",
                        "size": 2000,
                        "organism": {
                                "id": 9606,
                                "name": "Homo sapiens"
                        }
                }
        ],
        "venn_protein_mus": [
                {
                        "sets": [0],
                        "tooltipname": "Proteins",
                        "name": "Proteins",
                        "size": 22282,
                        "organism": {
                                "id": 10090,
                                "name": "Mus musculus"
                        }
                },
                {
                        "sets": [1],
                        "tooltipname": "Enzymes",
                        "name": "Enzymes",
                        "size": 8000,
                        "organism": {
                                "id": 10090,
                                "name": "Mus musculus"
                        }
                },
                {
                        "sets": [2],
                        "tooltipname": "Glycoproteins",
                        "name": "Glycoproteins",
                        "size": 3788,
                        "organism": {
                                "id": 10090,
                                "name": "Mus musculus"
                        }
                },
                {
                        "sets": [0, 1],
                        "tooltipname": "Enzymes",
                        "name": "",
                        "size": 8000,
                        "organism": {
                                "id": 10090,
                                "name": "Mus musculus"
                        }
                },
                {
                        "sets": [0, 2],
                        "tooltipname": "Glycoproteins",
                        "name": "",
                        "size": 3788,
                        "organism": {
                                "id": 10090,
                                "name": "Mus musculus"
                        }
                },
                {
                        "sets": [0, 1, 2],
                        "tooltipname": "Glycoproteins & Enzymes",
                        "name": "",
                        "size": 2000,
                        "organism": {
                                "id": 10090,
                                "name": "Mus musculus"
                        }
                }
        ],
        "venn_protein_rat": [
                {
                        "sets": [0],
                        "tooltipname": "Proteins",
                        "name": "Proteins",
                        "size": 21673,
                        "organism": {
                                "id": 10116,
                                "name": "Rattus norvegicus"
                        }
                },
                {
                        "sets": [1],
                        "tooltipname": "Enzymes",
                        "name": "Enzymes",
                        "size": 10000,
                        "organism": {
                                "id": 10116,
                                "name": "Rattus norvegicus"
                        }
                },
                {
                        "sets": [2],
                        "tooltipname": "Glycoproteins",
                        "name": "Glycoproteins",
                        "size": 2086,
                        "organism": {
                                "id": 10116,
                                "name": "Rattus norvegicus"
                        }
                },
                {
                        "sets": [0, 1],
                        "tooltipname": "Enzymes",
                        "name": "",
                        "size": 10000,
                        "organism": {
                                "id": 10116,
                                "name": "Rattus norvegicus"
                        }
                },
                {
                        "sets": [0, 2],
                        "tooltipname": "Glycoproteins",
                        "name": "",
                        "size": 2086,
                        "organism": {
                                "id": 10116,
                                "name": "Rattus norvegicus"
                        }
                },
                {
                        "sets": [0, 1, 2],
                        "tooltipname": "Glycoproteins & Enzymes",
                        "name": "",
                        "size": 2000,
                        "organism": {
                                "id": 10116,
                                "name": "Rattus norvegicus"
                        }
                }
        ],      
        "pie_glycohydrolases_prot": [
                {
                        "organism": {
                                "id": 9606,
                                "name": "Homo sapiens"
                        },
                        "name": "Human",
                        "size": 84
                },
                {
                        "organism": {
                                "id": 10090,
                                "name": "Mus musculus"
                        },
                        "name": "Mouse",
                        "size": 77
                },
                {
                        "organism": {
                                "id": 10116,
                                "name": "Rattus norvegicus"
                        },
                        "name": "Rat",
                        "size": 35
                }
        ],
        "pie_glycosyltransferases_prot": [
                {
                        "organism": {
                                "id": 9606,
                                "name": "Homo sapiens"
                        },
                        "name": "Human",
                        "size": 222
                },
                {
                        "organism": {
                                "id": 10090,
                                "name": "Mus musculus"
                        },
                        "name": "Mouse",
                        "size": 194
                },
                {
                        "organism": {
                                "id": 10116,
                                "name": "Rattus norvegicus"
                        },              
                        "name": "Rat",
                        "size": 94
                }
        ],
        "sunb_glycoprot_rep_pred_glyc": {       
                "name": "",
                "children": [{
                                "name": "Human Proteins",
                                "children": [{
                                                "organism": {
                                                        "id": 9606,
                                                        "name": "Homo sapiens"
                                                },
                                                "name": "Human RWGS",
                                                "size": 1084
                                        },
                                        {
                                                "organism": {
                                                        "id": 9606,
                                                        "name": "Homo sapiens"
                                                },
                                                "name": "Human RWOGS",
                                                "size": 700
                                        },
                                        {
                                                "organism": {
                                                        "id": 9606,
                                                        "name": "Homo sapiens"
                                                },
                                                "name": "Human Predicted",
                                                "size": 2946
                                        }                
                                ]
                        },
                        {
                                "name": "Mouse Proteins",
                                "children": [{
                                                "organism": {
                                                        "id": 10090,
                                                        "name": "Mus musculus"
                                                },
                                                "name": "Mouse RWGS",
                                                "size": 328
                                        },
                                        {
                                                "organism": {
                                                        "id": 10090,
                                                        "name": "Mus musculus"
                                                },
                                                "name": "Mouse RWOGS",
                                                "size": 200
                                        },
                                        {
                                                "organism": {
                                                        "id": 10090,
                                                        "name": "Mus musculus"
                                                },
                                                "name": "Mouse Predicted",
                                                "size": 3267
                                        }
                                ]
                        },
                        {
                                "name": "Rat Proteins",
                                "children": [{
                                                "organism": {
                                                        "id": 10116,
                                                        "name": "Rattus norvegicus"
                                                },
                                                "name": "Rat RWGS",
                                                "size": 151
                                        },
                                        {
                                                "organism": {
                                                        "id": 10116,
                                                        "name": "Rattus norvegicus"
                                                },
                                                "name": "Rat RWOGS",
                                                "size": 100
                                        },
                                        {
                                                "organism": {
                                                        "id": 10116,
                                                        "name": "Rattus norvegicus"
                                                },
                                                "name": "Rat Predicted",
                                                "size": 1840
                                        }
                                ]
                        }
                ]
        }
};

