import os
from src.summarizer import Summarizer

def test_post(summarizer, post, index=1):
    print(f"\nTesting post #{index}: {post['title']}")
    print("-" * 50)
    result = summarizer.summarize_post(post["content"], post["title"])
    
    print(f"Summary method used: {result['method']}")
    print("\nGenerated Summary:")
    print("-" * 50)
    print(result["summary"])
    print("\nTopic Classification:")
    print("-" * 50)
    print(result["topic"])
    print("\n" + "=" * 80 + "\n")

def main():
    # Test posts
    test_posts = [
        {
            "title": "Existing UDTs test the limits of Bayesianism (and consistency)",
            "content": """Epistemic status: Using UDT as a case study for the tools developed in my meta-theory of rationality sequence so far, which means all previous posts are prerequisites. This post is the result of conversations with many people at the CMU agent foundations conference, including particularly Daniel A. Herrmann, Ayden Mohensi, Scott Garrabrant, and Abram Demski.

The core problem of UDT is that it's trying to be consistent in a way that Bayesianism can't handle. Specifically:

1. UDT wants to make decisions that are consistent with the decisions it would make in other possible worlds
2. But Bayesianism can only handle uncertainty about what world you're in, not uncertainty about what decision you'll make
3. And if you try to be uncertain about your own decisions, you run into problems with self-reference

Let me explain each of these points in more detail:

First, UDT wants to make decisions that are consistent across possible worlds. This means that if you're deciding whether to cooperate or defect in a prisoner's dilemma, you want your decision to be consistent with what you would do if you were in the other player's position. You want to be the kind of agent who cooperates with other cooperators and defects against defectors.

Second, Bayesianism can only handle uncertainty about what world you're in. It can't handle uncertainty about what decision you'll make. This is because Bayesian probability theory is fundamentally about passive observation - you observe evidence and update your beliefs. But decision theory is about active intervention - you choose actions that affect the world.

Third, if you try to be uncertain about your own decisions, you run into problems with self-reference. This is because your decision depends on your beliefs about what decision you'll make, but your beliefs about what decision you'll make depend on your decision. This creates a circular dependency that can't be resolved within standard probability theory.

This is why UDT needs to go beyond Bayesianism. It needs a way to reason about decisions that:
1. Can handle consistency across possible worlds
2. Can deal with active intervention rather than just passive observation
3. Can resolve self-referential dependencies

The solution that UDT proposes is to treat decisions as logical facts rather than probabilistic beliefs. Instead of being uncertain about what decision you'll make, you prove theorems about what decision you would make under various circumstances. This avoids the circularity problem because logical implication is transitive - if A implies B and B implies C, then A implies C.""",
            "url": "https://www.lesswrong.com/posts/example2"
        },
        {
            "title": "The Most Forbidden Technique",
            "content": """The Most Forbidden Technique is training an AI using interpretability techniques. 
            An AI produces a final output [X] via some method [M]. You can analyze [M] using technique [T], 
            to learn what the AI is up to. You could train on that. Never do that. You train on [X]. 
            Only [X]. Never [M], never [T]. Why? Because [T] is how you figure out when the model is misbehaving.""",
            "url": "https://www.lesswrong.com/posts/example1"
        }
    ]

    # Initialize summarizer
    try:
        summarizer = Summarizer()
        print("Summarizer initialized successfully")
        
        # Test each post
        for i, post in enumerate(test_posts, 1):
            test_post(summarizer, post, i)
            
    except Exception as e:
        print(f"Error during test: {str(e)}")

if __name__ == "__main__":
    main() 