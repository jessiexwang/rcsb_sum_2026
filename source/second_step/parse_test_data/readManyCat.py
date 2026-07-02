



def readMoreCat(self, group, l_cat, id):
        """method to read the two categories+ their attributes needed

        Args:
            group (str): group that the entry belongs to
            id (str): dep id
            l_cat (str): list of categories to parse

        Returns:
            dict: dictionary of combined parsed info
        """
   
        d_new = {}      

        for item in l_cat:
            if item.contains("."):
                index = item.index(".")
                category = item[:index]

                d1 = workerOne_all(category, group, id)
                d_new[item] = d1[item]
            else:
                category = item
                d1 = workerOne_all(category, group, id)
                d_new.update(d1)
               