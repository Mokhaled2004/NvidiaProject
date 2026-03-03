import numpy as np

class SemanticGuardrail:
    def __init__(self, embeddings):
        self.embeddings = embeddings
        # Define topics that are strictly off-limits for the HR Assistant
        self.banned_topics = [
            "how to cook", "medical advice", "weather", "gaming", 
            "programming code", "jokes", "politics", "religion"
        ]
        # Pre-calculate embeddings for banned topics to save processing time
        self.banned_embeddings = [self.embeddings.embed_query(t) for t in self.banned_topics]

    def is_out_of_scope(self, query: str, threshold: float = 0.75):
        # Convert the user's question into a numerical vector
        query_vec = self.embeddings.embed_query(query)
        
        for banned_vec in self.banned_embeddings:
            # Calculate Cosine Similarity to see how 'close' the query is to a banned topic
            similarity = np.dot(query_vec, banned_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(banned_vec))
            
            # If the similarity exceeds the limit, flag the query as out-of-scope
            if similarity > threshold:
                return True
        return False