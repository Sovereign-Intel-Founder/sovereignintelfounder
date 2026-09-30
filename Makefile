.PHONY: all test sanitize lockfree_spsc_ring clean

all:
	$(MAKE) -C core all

test:
	$(MAKE) -C core test

sanitize:
	$(MAKE) -C core sanitize

lockfree_spsc_ring:
	$(MAKE) -C core lockfree_spsc_ring

clean:
	$(MAKE) -C core clean

.PHONY: audit
audit:
	python3 scripts/init_keys.py
	python3 adapters/sovereign_adapter_phase1.py
	python3 adapters/sovereign_adapter_phase2.py
	$(MAKE) -C core test
