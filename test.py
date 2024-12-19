from langchain.text_splitter import RecursiveCharacterTextSplitter

# Step 1: Load sample text
sample_question = "Control opacity in BrushLabels"
sample_text = "Thanks for the feature request @younesslanda! Our team will review it and see where it fits in our roadmap. \r\n\r\nAs an aside, how less painful would it be to have an opacity setting for the brushlabels when making annotations? "

# Step 2: Define a function to test chunking
def test_chunking(text, chunk_size, overlap):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
    chunks = splitter.split_text(text)
    return chunks

# Step 3: Run experiments with different chunk sizes and overlaps
chunk_sizes = [200, 300, 500]  # Define a range of chunk sizes
overlaps = [50, 100, 150]      # Define a range of overlaps

# Results storage
results = {}

for chunk_size in chunk_sizes:
    for overlap in overlaps:
        chunks = test_chunking(sample_question, chunk_size, overlap)
        results[(chunk_size, overlap)] = chunks
        print(f"\nChunk Size: {chunk_size}, Overlap: {overlap}")
        for i, chunk in enumerate(chunks):
            print(f"Chunk {i+1}: {chunk}")
for chunk_size in chunk_sizes:
    for overlap in overlaps:
        chunks = test_chunking(sample_text, chunk_size, overlap)
        results[(chunk_size, overlap)] = chunks
        print(f"\nChunk Size: {chunk_size}, Overlap: {overlap}")
        for i, chunk in enumerate(chunks):
            print(f"Chunk {i+1}: {chunk}")
