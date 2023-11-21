import pyfdl


def test_context_instance_from_dict(sample_context):
    ctx = pyfdl.Context.from_dict(sample_context)
    assert isinstance(ctx, pyfdl.Context)
    assert ctx.to_dict() == sample_context


def test_context_intsance_from_kwargs(sample_context):
    ctx = pyfdl.Context(**sample_context)
    assert isinstance(ctx, pyfdl.Context)
    assert ctx.to_dict() == sample_context
