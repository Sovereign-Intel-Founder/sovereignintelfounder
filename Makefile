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
	PYTHONPATH=$(PWD) python3 sovereign_workspace/scripts/init_keys.py
