from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import spacy
from typing import List

# Initialize FastAPI app
app = FastAPI(title="Entity Extraction Service")

# Load spaCy English model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    raise RuntimeError(
        "spaCy model 'en_core_web_sm' not found. "
        "Install it with: python -m spacy download en_core_web_sm"
    )


# Request model
class TextInput(BaseModel):
    text: str = Field(..., min_length=1, description="Text to extract entities from")


# Response models
class Entity(BaseModel):
    text: str
    label: str


class EntityResponse(BaseModel):
    entities: List[Entity]


@app.post("/extract_entities", response_model=EntityResponse)
def extract_entities(input_data: TextInput):
    """
    Extract named entities from the provided text.
    
    Supported entity types:
    - PERSON: People, including fictional
    - ORG: Organizations
    - GPE: Geopolitical entities (countries, cities, etc.)
    - And other spaCy entity types
    
    Args:
        input_data: JSON body with 'text' field
        
    Returns:
        JSON with list of entities containing text and label
    """
    try:
        text = input_data.text.strip()
        
        # Additional validation for empty or whitespace-only text
        if not text:
            raise ValueError("Text cannot be empty or contain only whitespace")
        
        # Process text with spaCy
        doc = nlp(text)
        
        # Extract entities
        entities = [
            Entity(text=ent.text, label=ent.label_)
            for ent in doc.ents
        ]
        
        return EntityResponse(entities=entities)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing text: {str(e)}")


@app.get("/")
def root():
    """Health check and documentation."""
    return {
        "message": "Entity Extraction Service",
        "endpoint": "/extract_entities",
        "method": "POST",
        "example": {
            "request": {"text": "Apple Inc. was founded by Steve Jobs in Cupertino, California."},
            "response": {
                "entities": [
                    {"text": "Apple Inc.", "label": "ORG"},
                    {"text": "Steve Jobs", "label": "PERSON"},
                    {"text": "Cupertino", "label": "GPE"},
                    {"text": "California", "label": "GPE"}
                ]
            }
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)
