"""Quick performance test for hand evaluator."""

import time

from texas_holdem_ml_bot.engine.cards import Deck
from texas_holdem_ml_bot.engine.evaluator import evaluate_hand


def test_performance():
    """Test evaluator performance with different hand counts."""

    # Test with different hand counts
    for num_hands in [100, 1000, 10000, 100000]:
        print(f"\nTesting {num_hands:,} hands...")

        start_time = time.time()

        for i in range(num_hands):
            # Create a fresh deck and draw 7 cards
            deck = Deck()
            deck.shuffle()
            cards = deck.draw(7)

            # Evaluate the hand
            category, kickers = evaluate_hand(cards)

        elapsed = time.time() - start_time
        per_hand_us = (elapsed / num_hands) * 1_000_000
        hands_per_second = num_hands / elapsed

        print(f"  Time: {elapsed:.3f}s")
        print(f"  Per hand: {per_hand_us:.2f} microseconds")
        print(f"  Throughput: {hands_per_second:,.0f} hands/second")

        # Check if performance is reasonable
        if per_hand_us > 1000:  # More than 1ms per hand is too slow
            print(f"  WARNING: Performance is poor ({per_hand_us:.0f}us per hand)")

    # Test 1 million hands
    print("\n" + "=" * 60)
    print("FINAL TEST: 1,000,000 hands")
    print("=" * 60)

    num_hands = 1_000_000
    start_time = time.time()

    for i in range(num_hands):
        if i % 100000 == 0 and i > 0:
            elapsed_so_far = time.time() - start_time
            print(f"  Progress: {i:,} hands in {elapsed_so_far:.1f}s...")

        deck = Deck()
        deck.shuffle()
        cards = deck.draw(7)
        evaluate_hand(cards)

    elapsed = time.time() - start_time
    per_hand_us = (elapsed / num_hands) * 1_000_000
    hands_per_second = num_hands / elapsed

    print("\nResults for 1,000,000 hands:")
    print(f"  Total time: {elapsed:.2f} seconds")
    print(f"  Per hand: {per_hand_us:.2f} microseconds")
    print(f"  Throughput: {hands_per_second:,.0f} hands/second")

    if elapsed < 30:
        print(f"  ✓ PASS: Completed in {elapsed:.1f}s (target: <30s)")
    else:
        print(f"  ✗ FAIL: Took {elapsed:.1f}s (target: <30s)")

    return elapsed


if __name__ == "__main__":
    test_performance()
