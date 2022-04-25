def get_info(artist:str, database):
    """
    Parameters:
    - artist is artist as a string,
    - database is artist collection

    This function retrieves all artist objects from the artists collection.
    """
    artistt = database.find({'stage_name':artist})
    return artistt
