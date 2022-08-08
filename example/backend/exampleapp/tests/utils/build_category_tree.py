from exampleapp.models import Category, Documentcategories


def build_category_tree():
    """
        Builds the following trees:
                      Category 1                                Category 2
                      /       \                                 /       \
               C.1.1             C.1.2                   C.2.1             C.2.2
               /   \             /   \                   /   \             /   \
         C.1.1.1  C.1.1.2   C.1.2.1  C.1.2.2       C.2.1.1  C.2.1.2   C.2.2.1  C.2.2.2
    """
    tree_desc = [
        {
            "Category 1": {
                "Category 1.1": {
                    "Category 1.1.1": {},
                    "Category 1.1.2": {},
                },
                "Category 1.2": {
                    "Category 1.2.1": {},
                    "Category 1.2.2": {},
                }
            },
        },
        {
            "Category 2": {
                "Category 2.1": {
                    "Category 2.1.1": {},
                    "Category 2.1.2": {},
                },
                "Category 2.2": {
                    "Category 2.2.1": {},
                    "Category 2.2.2": {},
                }
            }
        }
    ]

    # Iterate over it, breadth-first
    last_level = tree_desc
    depth = 0
    nodes_by_name = {}

    for item in last_level:
        for root in item:
            nodes_by_name[root] = Category.add_root(name=root)

    while len(last_level) != 0:
        for item in last_level:
            for parent, values in item.items():
                for child in values:
                    nodes_by_name[child] = nodes_by_name[parent].add_child(name=child)

        new_level = []
        for item in last_level:
            new_level += item.values()
        last_level = new_level

        depth += 1

    Documentcategories.objects.create(id=1, document_id=1, category=nodes_by_name["Category 1"])
    Documentcategories.objects.create(id=2, document_id=2, category=nodes_by_name["Category 1"])
    Documentcategories.objects.create(id=3, document_id=3, category=nodes_by_name["Category 1.1"])
    Documentcategories.objects.create(id=4, document_id=3, category=nodes_by_name["Category 1.2.1"])
    Documentcategories.objects.create(id=5, document_id=4, category=nodes_by_name["Category 1.1"])
    Documentcategories.objects.create(id=6, document_id=4, category=nodes_by_name["Category 1.2.2"])
    Documentcategories.objects.create(id=7, document_id=5, category=nodes_by_name["Category 1.2"])
    Documentcategories.objects.create(id=8, document_id=5, category=nodes_by_name["Category 1.1.1"])
    Documentcategories.objects.create(id=9, document_id=6, category=nodes_by_name["Category 1.1.2"])
    Documentcategories.objects.create(id=10, document_id=6, category=nodes_by_name["Category 1.2.2"])
    Documentcategories.objects.create(id=11, document_id=7, category=nodes_by_name["Category 1.1.1"])
    Documentcategories.objects.create(id=12, document_id=7, category=nodes_by_name["Category 1.2.1"])
    Documentcategories.objects.create(id=13, document_id=8, category=nodes_by_name["Category 1.1.1"])
    Documentcategories.objects.create(id=14, document_id=8, category=nodes_by_name["Category 1.2.2"])
    Documentcategories.objects.create(id=15, document_id=9, category=nodes_by_name["Category 1.1.1"])
    Documentcategories.objects.create(id=16, document_id=9, category=nodes_by_name["Category 1.2.2"])
    Documentcategories.objects.create(id=17, document_id=10, category=nodes_by_name["Category 1.2.1"])
    Documentcategories.objects.create(id=18, document_id=11, category=nodes_by_name["Category 1.1.2"])
    Documentcategories.objects.create(id=19, document_id=11, category=nodes_by_name["Category 1.1.1"])
    Documentcategories.objects.create(id=20, document_id=12, category=nodes_by_name["Category 1.2.2"])
    Documentcategories.objects.create(id=21, document_id=13, category=nodes_by_name["Category 1.1.1"])
    Documentcategories.objects.create(id=22, document_id=9, category=nodes_by_name["Category 2.1.1"])
    Documentcategories.objects.create(id=23, document_id=9, category=nodes_by_name["Category 2.2.2"])
    Documentcategories.objects.create(id=24, document_id=10, category=nodes_by_name["Category 2.2.1"])
    Documentcategories.objects.create(id=25, document_id=11, category=nodes_by_name["Category 2.1.2"])
    Documentcategories.objects.create(id=26, document_id=11, category=nodes_by_name["Category 2.1.1"])
    Documentcategories.objects.create(id=27, document_id=12, category=nodes_by_name["Category 2.2.2"])
    Documentcategories.objects.create(id=28, document_id=13, category=nodes_by_name["Category 2.1.1"])