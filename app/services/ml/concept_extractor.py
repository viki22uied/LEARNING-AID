import logging
from typing import List, Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    logger.warning("spaCy not available")

try:
    from keybert import KeyBERT
    KEYBERT_AVAILABLE = True
except ImportError:
    KEYBERT_AVAILABLE = False
    logger.warning("KeyBERT not available")


class ConceptExtractor:
    def __init__(self):
        self.nlp = None
        self.keybert_model = None
        self.initialized = False
        
    async def initialize(self):
        """Initialize the concept extractor"""
        try:
            if SPACY_AVAILABLE:
                # Load spaCy model
                try:
                    self.nlp = spacy.load("en_core_web_sm")
                except OSError:
                    logger.warning("spaCy model not found, downloading...")
                    spacy.cli.download("en_core_web_sm")
                    self.nlp = spacy.load("en_core_web_sm")
                logger.info("spaCy model loaded")
            
            if KEYBERT_AVAILABLE:
                # Initialize KeyBERT
                self.keybert_model = KeyBERT()
                logger.info("KeyBERT model loaded")
            
            self.initialized = True
            logger.info("Concept extractor initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize concept extractor: {e}")
            raise
    
    async def extract_concepts(self, text: str, max_concepts: int = 10) -> List[str]:
        """Extract key concepts from text"""
        if not self.initialized:
            await self.initialize()
        
        try:
            concepts = []
            
            # Extract concepts using different methods
            if KEYBERT_AVAILABLE and self.keybert_model:
                keybert_concepts = await self._extract_keybert_concepts(text, max_concepts // 2)
                concepts.extend(keybert_concepts)
            
            if SPACY_AVAILABLE and self.nlp:
                spacy_concepts = await self._extract_spacy_concepts(text, max_concepts // 2)
                concepts.extend(spacy_concepts)
            
            # Combine and deduplicate concepts
            combined_concepts = await self._deduplicate_concepts(concepts)
            
            # Score and rank concepts
            scored_concepts = await self._score_concepts(combined_concepts, text)
            
            # Return top concepts
            return [concept["text"] for concept in scored_concepts[:max_concepts]]
            
        except Exception as e:
            logger.error(f"Error extracting concepts: {e}")
            return []
    
    async def _extract_keybert_concepts(self, text: str, max_concepts: int) -> List[str]:
        """Extract concepts using KeyBERT"""
        try:
            # Extract keywords using KeyBERT
            keywords = self.keybert_model.extract_keywords(
                text,
                keyphrase_ngram_range=(1, 3),
                stop_words='english',
                use_maxsum=True,
                nr_candidates=max_concepts * 2,
                top_k=max_concepts
            )
            
            return [keyword for keyword, score in keywords]
            
        except Exception as e:
            logger.error(f"KeyBERT extraction error: {e}")
            return []
    
    async def _extract_spacy_concepts(self, text: str, max_concepts: int) -> List[str]:
        """Extract concepts using spaCy"""
        try:
            doc = self.nlp(text)
            concepts = []
            
            # Extract named entities
            for ent in doc.ents:
                if ent.label_ in ["PERSON", "ORG", "GPE", "PRODUCT", "EVENT", "WORK_OF_ART"]:
                    concepts.append(ent.text.strip())
            
            # Extract noun phrases
            for chunk in doc.noun_chunks:
                if len(chunk.text.split()) <= 3:  # Limit to 3-word phrases
                    concepts.append(chunk.text.strip())
            
            # Extract important nouns and adjectives
            for token in doc:
                if (token.pos_ in ["NOUN", "PROPN"] and 
                    not token.is_stop and 
                    len(token.text) > 2):
                    concepts.append(token.text.strip())
            
            return concepts[:max_concepts]
            
        except Exception as e:
            logger.error(f"spaCy extraction error: {e}")
            return []
    
    async def _deduplicate_concepts(self, concepts: List[str]) -> List[Dict[str, Any]]:
        """Deduplicate and normalize concepts"""
        seen = set()
        unique_concepts = []
        
        for concept in concepts:
            # Normalize concept
            normalized = concept.lower().strip()
            
            if normalized and normalized not in seen:
                seen.add(normalized)
                unique_concepts.append({
                    "text": concept.strip(),
                    "normalized": normalized,
                    "length": len(concept),
                    "word_count": len(concept.split())
                })
        
        return unique_concepts
    
    async def _score_concepts(self, concepts: List[Dict[str, Any]], text: str) -> List[Dict[str, Any]]:
        """Score concepts based on relevance and importance"""
        text_lower = text.lower()
        
        for concept in concepts:
            score = 0.0
            
            # Frequency score
            frequency = text_lower.count(concept["normalized"])
            score += min(frequency * 0.1, 0.5)  # Cap at 0.5
            
            # Length score (prefer medium-length concepts)
            length_score = 1.0 - abs(concept["word_count"] - 2) * 0.2
            score += max(length_score, 0.0)
            
            # Educational relevance score
            educational_keywords = [
                "learning", "education", "teaching", "study", "research",
                "theory", "method", "technique", "approach", "concept",
                "principle", "framework", "model", "system", "process"
            ]
            
            if any(keyword in concept["normalized"] for keyword in educational_keywords):
                score += 0.3
            
            concept["score"] = score
        
        # Sort by score (descending)
        concepts.sort(key=lambda x: x["score"], reverse=True)
        
        return concepts
    
    async def extract_educational_concepts(self, text: str, max_concepts: int = 5) -> List[str]:
        """Extract education-specific concepts"""
        try:
            all_concepts = await self.extract_concepts(text, max_concepts * 2)
            
            # Filter for educational relevance
            educational_concepts = []
            educational_patterns = [
                "learning", "education", "teaching", "student", "teacher",
                "course", "lesson", "lecture", "assignment", "homework",
                "exam", "test", "quiz", "grade", "score", "assessment",
                "curriculum", "syllabus", "textbook", "reference", "resource"
            ]
            
            for concept in all_concepts:
                concept_lower = concept.lower()
                if any(pattern in concept_lower for pattern in educational_patterns):
                    educational_concepts.append(concept)
            
            return educational_concepts[:max_concepts]
            
        except Exception as e:
            logger.error(f"Error extracting educational concepts: {e}")
            return []
    
    async def extract_subject_areas(self, text: str) -> List[str]:
        """Extract subject areas from text"""
        subject_areas = []
        
        # Define subject area keywords
        subject_keywords = {
            "mathematics": ["math", "mathematics", "algebra", "calculus", "geometry", "statistics", "trigonometry"],
            "physics": ["physics", "mechanics", "thermodynamics", "quantum", "relativity", "optics", "electromagnetism"],
            "chemistry": ["chemistry", "organic", "inorganic", "biochemistry", "molecular", "atomic", "chemical"],
            "biology": ["biology", "genetics", "evolution", "ecology", "microbiology", "anatomy", "physiology"],
            "computer_science": ["computer", "programming", "algorithm", "software", "database", "network", "artificial intelligence"],
            "history": ["history", "historical", "ancient", "medieval", "modern", "civilization", "war"],
            "literature": ["literature", "poetry", "novel", "drama", "fiction", "author", "writing"],
            "philosophy": ["philosophy", "ethics", "logic", "metaphysics", "epistemology", "moral", "reasoning"],
            "economics": ["economics", "economic", "market", "trade", "finance", "business", "commerce"],
            "psychology": ["psychology", "psychological", "behavior", "cognitive", "mental", "therapy"]
        }
        
        text_lower = text.lower()
        
        for subject, keywords in subject_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                subject_areas.append(subject)
        
        return subject_areas[:3]  # Return top 3 subject areas


# Global instance
concept_extractor = ConceptExtractor()
