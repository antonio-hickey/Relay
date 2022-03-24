from typing import Optional, Type

from pynamodb.indexes import AllProjection, Projection

from app.config import AWS_ACCESS_KEY, AWS_SECRET_KEY

all_projections = AllProjection()


def pynamodb_table_meta(title: str) -> Type:
    """Render meta class for dynamodb."""
    class Meta:
        table_name: str = title
        region: str = "us-east-1"
        read_capacity_units: int = 1
        write_capacity_units: int = 1
        aws_access_key_id: str = AWS_ACCESS_KEY
        aws_secret_access_key: str = AWS_SECRET_KEY

    return Meta


def pynamodb_index_meta(*,
                        hash_key: str,
                        range_key: Optional[str],
                        projection: Projection = AllProjection()) -> Type:
    """idk yet"""
    meta = pynamodb_unamed_index_meta(projection=projection)
    if range_key:
        meta.index_name = f"{hash_key}-{range_key}-index"
    else:
        meta.index_name = f"{hash_key}-index"
    return meta


def pynamodb_unamed_index_meta(projection: Projection = AllProjection()) -> Type:
    _projection: Projection = projection

    class Meta:
        projection: Projection = _projection
        region: str = "us-east-1"
        read_capacity_units: int = 1
        write_capacity_units: int = 1

    return Meta
