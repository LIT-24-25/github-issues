my_model = None
my_chroma = None

def initialize_instances():
    from business_logic.train import create_model
    from business_logic.mychroma import MyChroma
    global my_model, my_chroma
    my_model = create_model()
    my_chroma = MyChroma(my_model)