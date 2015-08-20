"""Universally used library functions."""

def MergeModelsToDict(*models, **kwargs):
  for mod in models:
    kwargs.update(mod.to_dict())
  return kwargs
