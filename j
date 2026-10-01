{"id":"e5e9e8999a3451a947eb2f05508b4a29","offset":1,"sort":"hit_score","limit":20,"order":"desc","filters":[],"columns":["uniprot_canonical_ac","protein_name","organism","hit_score","start_pos","end_pos","gene_name"]}




				if query_obj["evidence_type"] == "all_sites":
                cond_objs.append({"glycosylation": {'$gt': []}})
            elif query_obj["evidence_type"] == "sites_reported_with_glycans":
                oo = {"glycosylation.site_category_dict.reported_with_glycan":{"$eq":True}}
                cond_objs.append(oo)
            elif query_obj["evidence_type"] == "sites_reported_without_glycans":
                oo = {"glycosylation.site_category_dict.reported":{"$eq":True}}
                cond_objs.append(oo)
            elif query_obj["evidence_type"] == "all_reported_sites_with_without_glycans":
                or_list = [
                    {"glycosylation.site_category_dict.reported_with_glycan":{"$eq":True}},
                    {"glycosylation.site_category_dict.reported":{"$eq":True}}
                ]
                cond_objs.append({"$or":or_list})
            elif query_obj["evidence_type"] == "sites_detected_by_literature_mining":
                oo = {"glycosylation.site_category_dict.automatic_literature_mining":{"$eq":True}}
                cond_objs.append(oo)
            elif query_obj["evidence_type"] == "predicted_sites":
                oo = {"glycosylation.site_category_dict.predicted":{"$eq":True}},
                cond_objs.append(oo)
