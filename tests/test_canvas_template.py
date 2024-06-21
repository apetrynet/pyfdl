import pytest

import pyfdl


def test_canvas_template_from_dict(sample_canvas_template):
    canvas_template = pyfdl.CanvasTemplate.from_dict(sample_canvas_template)
    assert isinstance(canvas_template, pyfdl.CanvasTemplate)
    assert canvas_template.to_dict() == sample_canvas_template


def test_canvas_template_from_kwargs(sample_canvas_template, sample_canvas_template_kwargs):
    canvas_template = pyfdl.CanvasTemplate(**sample_canvas_template_kwargs)
    assert isinstance(canvas_template, pyfdl.CanvasTemplate)
    assert canvas_template.to_dict() == sample_canvas_template


def test_fit_source_enum_validation(sample_canvas_template):
    faulty_value = 'thisisnotvalid'
    canvas_template = pyfdl.CanvasTemplate()

    canvas_template.fit_source = sample_canvas_template['fit_source']
    assert canvas_template.fit_source == sample_canvas_template['fit_source']

    with pytest.raises(pyfdl.FDLError) as err:
        canvas_template.fit_source = faulty_value

    assert f'"{faulty_value}" is not a valid option for "fit_source"' in str(err.value)


def test_fit_method_enum_validation(sample_canvas_template):
    faulty_value = 'thisisnotvalid'
    canvas_template = pyfdl.CanvasTemplate()

    canvas_template.fit_method = sample_canvas_template['fit_method']
    assert canvas_template.fit_method == sample_canvas_template['fit_method']

    with pytest.raises(pyfdl.FDLError) as err:
        canvas_template.fit_method = faulty_value

    assert f'"{faulty_value}" is not a valid option for "fit_method"' in str(err.value)


def test_alignment_method_vertical_enum_validation(sample_canvas_template):
    faulty_value = 'thisisnotvalid'
    canvas_template = pyfdl.CanvasTemplate()

    canvas_template.alignment_method_vertical = sample_canvas_template['alignment_method_vertical']
    assert canvas_template.alignment_method_vertical == sample_canvas_template['alignment_method_vertical']

    with pytest.raises(pyfdl.FDLError) as err:
        canvas_template.alignment_method_vertical = faulty_value

    assert f'"{faulty_value}" is not a valid option for "alignment_method_vertical"' in str(err.value)


def test_alignment_method_horizontal_enum_validation(sample_canvas_template):
    faulty_value = 'thisisnotvalid'
    canvas_template = pyfdl.CanvasTemplate()

    canvas_template.alignment_method_horizontal = sample_canvas_template['alignment_method_horizontal']
    assert canvas_template.alignment_method_horizontal == sample_canvas_template['alignment_method_horizontal']

    with pytest.raises(pyfdl.FDLError) as err:
        canvas_template.alignment_method_horizontal = faulty_value

    assert f'"{faulty_value}" is not a valid option for "alignment_method_horizontal"' in str(err.value)


def test_preserve_from_source_canvas_enum_validation(sample_canvas_template):
    faulty_value = 'thisisnotvalid'
    canvas_template = pyfdl.CanvasTemplate()

    canvas_template.preserve_from_source_canvas = sample_canvas_template['preserve_from_source_canvas']
    assert canvas_template.preserve_from_source_canvas == sample_canvas_template['preserve_from_source_canvas']

    with pytest.raises(pyfdl.FDLError) as err:
        canvas_template.preserve_from_source_canvas = faulty_value

    assert f'"{faulty_value}" is not a valid option for "preserve_from_source_canvas"' in str(err.value)

# TODO: Add more tests for all the variations of fit_methods etc.
