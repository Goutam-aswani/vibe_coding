import pytest
from fastapi.testclient import TestClient
from app import app


client = TestClient(app)


class TestExtractEntities:
    """Test suite for /extract_entities endpoint"""
    
    def test_extract_entities_success(self):
        """Test successful entity extraction with standard input"""
        response = client.post(
            "/extract_entities",
            json={"text": "Apple Inc. was founded by Steve Jobs in Cupertino, California."}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "entities" in data
        assert isinstance(data["entities"], list)
        assert len(data["entities"]) > 0
        
        # Check that expected entities are present
        texts = [ent["text"] for ent in data["entities"]]
        labels = [ent["label"] for ent in data["entities"]]
        
        assert "Apple Inc." in texts or "Apple" in texts
        assert "Steve Jobs" in texts
        assert "ORG" in labels
        assert "PERSON" in labels
    
    def test_extract_entities_with_multiple_types(self):
        """Test extraction of different entity types"""
        response = client.post(
            "/extract_entities",
            json={"text": "Barack Obama was the President of the United States. He worked at the White House in Washington, D.C."}
        )
        
        assert response.status_code == 200
        data = response.json()
        entities = data["entities"]
        
        labels = [ent["label"] for ent in entities]
        assert "PERSON" in labels
        assert "GPE" in labels
    
    def test_extract_entities_no_entities(self):
        """Test with text that has no named entities"""
        response = client.post(
            "/extract_entities",
            json={"text": "The quick brown fox jumps over the lazy dog."}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return empty entities list
        assert data["entities"] == []
    
    def test_empty_text_input(self):
        """Test with empty text input"""
        response = client.post(
            "/extract_entities",
            json={"text": ""}
        )
        
        assert response.status_code == 400
        assert "detail" in response.json()
    
    def test_whitespace_only_text(self):
        """Test with whitespace-only text"""
        response = client.post(
            "/extract_entities",
            json={"text": "   \n\t  "}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "whitespace" in data["detail"].lower() or "empty" in data["detail"].lower()
    
    def test_missing_text_field(self):
        """Test with missing text field"""
        response = client.post(
            "/extract_entities",
            json={}
        )
        
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_invalid_json(self):
        """Test with invalid JSON"""
        response = client.post(
            "/extract_entities",
            data="invalid json"
        )
        
        assert response.status_code == 422
    
    def test_long_text_input(self):
        """Test with long text input"""
        long_text = """
        Microsoft was founded by Bill Gates and Paul Allen in Seattle, Washington.
        Steve Jobs founded Apple Computer Company in Los Altos, California.
        Google was founded by Larry Page and Sergey Brin at Stanford University in Palo Alto.
        Amazon was founded by Jeff Bezos in Seattle.
        """
        
        response = client.post(
            "/extract_entities",
            json={"text": long_text}
        )
        
        assert response.status_code == 200
        data = response.json()
        entities = data["entities"]
        
        assert len(entities) > 0
        # Verify all entities have required fields
        for entity in entities:
            assert "text" in entity
            assert "label" in entity
            assert isinstance(entity["text"], str)
            assert isinstance(entity["label"], str)
    
    def test_response_format(self):
        """Test response format matches specification"""
        response = client.post(
            "/extract_entities",
            json={"text": "Google is in California."}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert isinstance(data, dict)
        assert "entities" in data
        assert isinstance(data["entities"], list)
        
        # Verify each entity
        for entity in data["entities"]:
            assert set(entity.keys()) == {"text", "label"}
            assert isinstance(entity["text"], str)
            assert isinstance(entity["label"], str)
    
    def test_root_endpoint(self):
        """Test root endpoint returns help information"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "endpoint" in data
        assert "example" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
