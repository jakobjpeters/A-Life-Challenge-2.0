def terrain_path(origin, destination, n = 5, terrain_restriction = "", predecessor = {}, visited = []):        
        """                                                                         
        Determens if there is a path to a certain place given terrain restrictions.     
        """                                                                             

        if origin == destination:                                               
            return True                                                                                                          
        #current_neighbours = []
                                                             
        #print(visited)
        if origin not in visited:
                                                            
            visited.append(origin)     
            #if n >= 0:
            adjacents = adjacent_move(origin, visited, terrain_restriction)
            print(adjacents)
            if adjacents !=[]:
                for adjacent in adjacents:
                    #if adjacent == destination:
                    #    return True

                    print(adjacent)
                    return terrain_path(adjacent, destination, n - 1, terrain_restriction, predecessor, visited)
        print(visited)
        return False
        
        
#def get_terrain(square):                      
#        return terrain[square[1]][square[0]]       

def adjacent_move(position, visited, terrain_restriction):
    """
    Get adjacent legal moves.                                                                                                                        
    """
    x = position[0]
    y = position[1] 

    adjactent_places = []   
    for i in [-1, 1]:                                           
        if y + i >= 0 and y + i < 50 and (x, y + i):# not in visited:      #     (adj_x, position[1]) not in pathed and (adj_x, position[1]) not in current_path:
            adjactent_places.append((x, y + i))                                                                 

        if x + i >= 0 and x + i < 50 and (x + i, y):# not in visited: #(position[0], adj_y) not in pathed and (position[0], adj_y) not in current_path:
            adjactent_places.append((x + i, y))    

    return adjactent_places