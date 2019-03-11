# -*- coding: utf-8 -*-
import io

import pandas as pd
import pytest

from isic_challenge_scoring import task3
from isic_challenge_scoring.scoreCommon import ScoreException


def test_parseCsv():
    predictionFileStream = io.StringIO(
        'image,MEL,NV,BCC,AKIEC,BKL,DF,VASC\n'
        'ISIC_0000123,1.0,0.0,0.0,0.0,0.0,0.0,0.0\n'
        'ISIC_0000124,0.0,1.0,0.0,0.0,0.0,0.0,0.0\n'
        'ISIC_0000125,0.0,0.0,1.0,0.0,0.0,0.0,0.0\n'
    )

    predictionProbabilities = task3.parseCsv(predictionFileStream)

    assert predictionProbabilities.equals(pd.DataFrame([
        [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0]
    ], index=['ISIC_0000123', 'ISIC_0000124', 'ISIC_0000125'], columns=task3.CATEGORIES))


def test_parseCsv_missingColumns():
    predictionFileStream = io.StringIO(
        'image,MEL,BCC,AKIEC,BKL,DF\n'
        'ISIC_0000123,1.0,0.0,0.0,0.0,0.0\n'
    )

    with pytest.raises(ScoreException) as excInfo:
        task3.parseCsv(predictionFileStream)

    assert 'Missing columns in CSV: [\'NV\', \'VASC\'].' == str(excInfo.value)


def test_parseCsv_extraColumns():
    predictionFileStream = io.StringIO(
        'image,MEL,FOO,NV,BCC,AKIEC,BKL,DF,BAZ,VASC\n'
        'ISIC_0000123,1.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0\n'
    )

    with pytest.raises(ScoreException) as excInfo:
        task3.parseCsv(predictionFileStream)

    assert 'Extra columns in CSV: [\'BAZ\', \'FOO\'].' == str(excInfo.value)


def test_parseCsv_misnamedColumns():
    predictionFileStream = io.StringIO(
        'image,MEL,FOO,BCC,AKIEC,BKL,BAZ,VASC\n'
        'ISIC_0000123,1.0,0.0,0.0,0.0,0.0,0.0,0.0\n'
    )

    with pytest.raises(ScoreException) as excInfo:
        task3.parseCsv(predictionFileStream)

    assert 'Missing columns in CSV: [\'DF\', \'NV\'].' == str(excInfo.value)


def test_parseCsv_reorderedColumns():
    predictionFileStream = io.StringIO(
        'NV,BCC,BKL,DF,AKIEC,MEL,VASC,image\n'
        '0.0,0.0,0.0,0.0,0.0,1.0,0.0,ISIC_0000123\n'
    )

    predictionProbabilities = task3.parseCsv(predictionFileStream)

    assert predictionProbabilities.equals(pd.DataFrame([
        [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    ], index=['ISIC_0000123'], columns=task3.CATEGORIES))


def test_parseCsv_missingIndex():
    predictionFileStream = io.StringIO(
        'MEL,NV,BCC,AKIEC,BKL,DF,VASC\n'
        '1.0,0.0,0.0,0.0,0.0,0.0,0.0\n'
    )

    with pytest.raises(ScoreException) as excInfo:
        task3.parseCsv(predictionFileStream)

    assert 'Missing column in CSV: "image".' == str(excInfo.value)


def test_parseCsv_missingValues():
    predictionFileStream = io.StringIO(
        'image,MEL,NV,BCC,AKIEC,BKL,DF,VASC\n'
        'ISIC_0000123,1.0,0.0,0.0,0.0,0.0,0.0,0.0\n'
        'ISIC_0000124,0.0,,0.0,0.0,0.0,0.0,0.0\n'
        'ISIC_0000125,0.0,0.0,1.0,0.0,0.0,0.0\n'
    )

    with pytest.raises(ScoreException) as excInfo:
        task3.parseCsv(predictionFileStream)

    assert 'Missing value(s) in CSV for images: [\'ISIC_0000124\', \'ISIC_0000125\'].' \
        == str(excInfo.value)


def test_parseCsv_nonFloatColumns():
    predictionFileStream = io.StringIO(
        'image,MEL,NV,BCC,AKIEC,BKL,DF,VASC\n'
        'ISIC_0000123,1.0,0.0,0.0,0.0,0.0,0.0,0.0\n'
        'ISIC_0000124,0.0,1.0,0.0,0.0,0.0,0.0,\'BAD\'\n'
        'ISIC_0000125,0.0,0.0,True,0.0,0.0,0.0,0.0\n'
    )

    with pytest.raises(ScoreException) as excInfo:
        task3.parseCsv(predictionFileStream)

    assert 'CSV contains non-floating-point value(s) in columns: [\'BCC\', \'VASC\'].' \
        == str(excInfo.value)


def test_parseCsv_outOfRangeValues():
    predictionFileStream = io.StringIO(
        'image,MEL,NV,BCC,AKIEC,BKL,DF,VASC\n'
        'ISIC_0000123,100.0,0.0,0.0,0.0,0.0,0.0,0.0\n'
        'ISIC_0000124,0.0,1.0,0.0,0.0,0.0,0.0,0.0\n'
        'ISIC_0000125,0.0,0.0,-1.0,0.0,0.0,0.0,0.0\n'
    )

    with pytest.raises(ScoreException) as excInfo:
        task3.parseCsv(predictionFileStream)

    assert 'Values in CSV are outside the interval [0.0, 1.0] for images: ' \
        '[\'ISIC_0000123\', \'ISIC_0000125\'].' == str(excInfo.value)


def test_excludeRows():
    probabilities = pd.DataFrame([
        [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0]
    ], index=['ISIC_0000123', 'ISIC_0000124', 'ISIC_0000125'], columns=task3.CATEGORIES)

    assert probabilities.shape == (3, 7)
    task3.excludeRows(probabilities, ['ISIC_0000123', 'ISIC_0000125'])
    assert probabilities.shape == (1, 7)
    task3.excludeRows(probabilities, ['ISIC_0000123'])
    assert probabilities.shape == (1, 7)


def test_validateRows_missingImages():
    truthProbabilities = pd.DataFrame([
        [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    ], index=['ISIC_0000123', 'ISIC_0000124'], columns=task3.CATEGORIES)
    predictionProbabilities = pd.DataFrame([
        [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    ], index=['ISIC_0000123', 'ISIC_0000124'], columns=task3.CATEGORIES)
    task3.validateRows(truthProbabilities, predictionProbabilities)

    truthProbabilities = pd.DataFrame([
        [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    ], index=['ISIC_0000123', 'ISIC_0000124'], columns=task3.CATEGORIES)
    predictionProbabilities = pd.DataFrame([
        [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    ], index=['ISIC_0000123'], columns=task3.CATEGORIES)
    with pytest.raises(ScoreException) as excInfo:
        task3.validateRows(truthProbabilities, predictionProbabilities)
    assert 'Missing images in CSV: [\'ISIC_0000124\'].' == str(excInfo.value)

    truthProbabilities = pd.DataFrame([
        [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    ], index=['ISIC_0000123', 'ISIC_0000124'], columns=task3.CATEGORIES)
    predictionProbabilities = pd.DataFrame([
        [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    ], index=['ISIC_0000120'], columns=task3.CATEGORIES)
    with pytest.raises(ScoreException) as excInfo:
        task3.validateRows(truthProbabilities, predictionProbabilities)
    assert 'Missing images in CSV: [\'ISIC_0000123\', \'ISIC_0000124\'].' == str(excInfo.value)

    truthProbabilities = pd.DataFrame([
        [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    ], index=['ISIC_0000123', 'ISIC_0000124'], columns=task3.CATEGORIES)
    predictionProbabilities = pd.DataFrame([
        [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    ], index=['ISIC_0000123', 'ISIC_0000125'], columns=task3.CATEGORIES)
    with pytest.raises(ScoreException) as excInfo:
        task3.validateRows(truthProbabilities, predictionProbabilities)
    assert 'Missing images in CSV: [\'ISIC_0000124\'].' == str(excInfo.value)


def test_validateRows_extraImages():
    truthProbabilities = pd.DataFrame([
        [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    ], index=['ISIC_0000123'], columns=task3.CATEGORIES)
    predictionProbabilities = pd.DataFrame([
        [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0]
    ], index=['ISIC_0000123', 'ISIC_0000126', 'ISIC_0000127'], columns=task3.CATEGORIES)
    with pytest.raises(ScoreException) as excInfo:
        task3.validateRows(truthProbabilities, predictionProbabilities)
    assert 'Extra images in CSV: [\'ISIC_0000126\', \'ISIC_0000127\'].' == str(excInfo.value)


def test_sortRows():
    predictionProbabilities = pd.DataFrame([
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    ], index=['ISIC_0000124', 'ISIC_0000125', 'ISIC_0000123'], columns=task3.CATEGORIES)

    task3.sortRows(predictionProbabilities)

    assert predictionProbabilities.equals(pd.DataFrame([
        [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0]
    ], index=['ISIC_0000123', 'ISIC_0000124', 'ISIC_0000125'], columns=task3.CATEGORIES))
