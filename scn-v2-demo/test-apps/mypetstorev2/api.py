from pets import *

def getPetById(petId): 
    print(f"petId={petId}")
    return getPetByIdImpl(petId)