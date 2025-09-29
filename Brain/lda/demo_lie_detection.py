#!/usr/bin/env python3
"""
Demo script showing the lie detection and logging functionality in the LDA system.

This script demonstrates:
1. How lies are detected during interviews
2. How nudging prompts candidates to elaborate  
3. How lies and elaborations are logged in interview summaries

Usage:
    python demo_lie_detection.py
"""

import json
from typing import Dict, List

from agents import ClaimAnalysis


def demonstrate_lie_detection_flow() -> None:
    """Demonstrate the complete lie detection and logging flow."""
    print("🎯 LDA Lie Detection & Logging Demo")
    print("=" * 50)
    
    # Simulate a detected lie
    print("\n1. 📊 Lie Detection Phase")
    print("-" * 30)
    
    detected_lie = ClaimAnalysis(
        claim="I worked as a Senior Software Engineer at Google for 5 years",
        lie=True,
        confidence=0.95,
        reasoning="Resume shows 2 years at Microsoft as Junior Developer, not 5 years at Google as Senior",
        category="experience"
    )
    
    print(f"🚨 Lie Detected:")
    print(f"   Claim: '{detected_lie.claim}'")
    print(f"   Confidence: {detected_lie.confidence:.2f}")
    print(f"   Reasoning: {detected_lie.reasoning}")
    print(f"   Category: {detected_lie.category}")
    
    # Simulate nudging and candidate response
    print("\n2. 🤔 Nudging Phase")
    print("-" * 20)
    
    nudge_text = "I need to pause here for a moment. You mentioned working as a Senior Software Engineer at Google for 5 years, but this doesn't seem to align with the information I have. Could you please walk me through this again?"
    
    print(f"🎙️  Interviewer Nudge:")
    print(f"   '{nudge_text}'")
    
    # Simulate candidate elaboration
    candidate_elaboration = "Oh, I apologize for the confusion. I meant to say I worked at Microsoft for 2 years as a Junior Developer. I was thinking about my aspiration to work at Google someday, and I misspoke. My actual experience is 2 years at Microsoft."
    
    print(f"\n🗣️  Candidate Elaboration:")
    print(f"   '{candidate_elaboration}'")
    
    # Simulate logging
    print("\n3. 📝 Logging Phase")
    print("-" * 20)
    
    # Create the lie entry as it would be stored
    lie_entry = {
        "lie": detected_lie.claim,
        "explanation_given_by_candidate": candidate_elaboration,
        "confidence": detected_lie.confidence,
        "reasoning": detected_lie.reasoning,
        "category": detected_lie.category
    }
    
    # Simulate complete interview summary
    interview_summary = {
        "summary": {
            "overall_summary": "Candidate showed some confusion about their work history but provided clarification when prompted.",
            "strengths": ["Willing to clarify mistakes", "Honest when corrected"],
            "areas_for_improvement": ["Accuracy in initial responses", "Attention to detail"],
            "hiring_recommendation": "Hire with Reservations"
        },
        "conversation_history": [
            {"role": "interviewer", "content": "Tell me about your work experience"},
            {"role": "candidate", "content": detected_lie.claim},
            {"role": "interviewer", "content": nudge_text},
            {"role": "candidate", "content": candidate_elaboration}
        ],
        "knowledge_base": {
            "entries": [
                {
                    "claim": "Junior Developer at Microsoft (2 years)",
                    "source": "resume",
                    "category": "experience"
                }
            ]
        },
        "lies": [lie_entry]  # This is the new key we added!
    }
    
    print("📊 Interview Summary Structure:")
    print(json.dumps(interview_summary, indent=2))
    
    print(f"\n✅ Lies Detected: {len(interview_summary['lies'])}")
    print(f"✅ Elaborations Captured: {len([lie for lie in interview_summary['lies'] if lie['explanation_given_by_candidate'] != '(No elaboration provided)'])}")


def demonstrate_multiple_lies() -> None:
    """Demonstrate handling multiple lies in one interview."""
    print("\n\n🔥 Multiple Lies Scenario")
    print("=" * 30)
    
    lies_detected = [
        {
            "lie": "I have 10 years of Python experience",
            "explanation_given_by_candidate": "Actually, it's 3 years. I was including the time I was learning it in college.",
            "confidence": 0.88,
            "reasoning": "Resume shows 3 years professional Python experience",
            "category": "skills"
        },
        {
            "lie": "I led a team of 50 developers at Amazon",
            "explanation_given_by_candidate": "I meant to say I was part of a team of 50, not leading it. I was a team lead for 3 people.",
            "confidence": 0.92,
            "reasoning": "Resume shows Team Lead role for small team, not 50 developers",
            "category": "experience"
        },
        {
            "lie": "I have a PhD in Computer Science from MIT",
            "explanation_given_by_candidate": "(No elaboration provided)",
            "confidence": 0.99,
            "reasoning": "Resume shows Bachelor's degree from state university",
            "category": "education"
        }
    ]
    
    print(f"📊 Total Lies Detected: {len(lies_detected)}")
    print(f"📊 Lies with Elaboration: {len([lie for lie in lies_detected if lie['explanation_given_by_candidate'] != '(No elaboration provided)'])}")
    print(f"📊 Lies without Elaboration: {len([lie for lie in lies_detected if lie['explanation_given_by_candidate'] == '(No elaboration provided)'])}")
    
    print("\n📝 Lies Summary:")
    for i, lie in enumerate(lies_detected, 1):
        print(f"\n  Lie #{i}:")
        print(f"    Claim: {lie['lie']}")
        print(f"    Elaboration: {lie['explanation_given_by_candidate']}")
        print(f"    Confidence: {lie['confidence']:.2f}")
        print(f"    Category: {lie['category']}")


def demonstrate_json_structure() -> None:
    """Show the exact JSON structure that will be saved."""
    print("\n\n📄 Final JSON Log Structure")
    print("=" * 35)
    
    example_log = {
        "summary": "{ ... final interview review ... }",
        "conversation_history": "[ ... full conversation ... ]", 
        "knowledge_base": "{ ... candidate data ... }",
        "lies": [
            {
                "lie": "string - the false claim made",
                "explanation_given_by_candidate": "string - their elaboration or '(No elaboration provided)'",
                "confidence": "float - confidence score 0-1",
                "reasoning": "string - why it was flagged as a lie", 
                "category": "string - experience|education|skills|personal|other"
            }
        ]
    }
    
    print("🗂️  New 'lies' key structure:")
    print(json.dumps(example_log, indent=2))


if __name__ == "__main__":
    print("🚀 Starting LDA Lie Detection Demo...")
    
    try:
        demonstrate_lie_detection_flow()
        demonstrate_multiple_lies()
        demonstrate_json_structure()
        
        print("\n\n🎉 Demo Complete!")
        print("\nKey Features Implemented:")
        print("✅ Lie detection during interviews")
        print("✅ Automatic nudging when lies are detected")  
        print("✅ Capture candidate elaborations/explanations")
        print("✅ Log lies with full context in interview summaries")
        print("✅ Support for multiple lies per interview")
        print("✅ Handle cases where no elaboration is provided")
        print("✅ Rich context (confidence, reasoning, category) for each lie")
        print("✅ Fallback detection when interviews end before nudging")
        print("✅ Capture lies detected in interviewer evaluations")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
