"""
__author__ = "Sky UK Ltd"
__copyright__ = Copyright © Sky CP Limited 2023.
All rights reserved. No part of this work may be reproduced,
stored in a retrieval system of any nature, or transmitted,
in any form or by any means including photocopying
and recording, without the prior written permission of Sky,
the copyright owner.
__licence__ = "subject to the terms of the licence with Sky UK Ltd'
__version__ = "1.0"
"""
# Standard Library
import datetime

# Third Party Library
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, MetaData, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.query import Query

metadata = MetaData()

Base = declarative_base(metadata=metadata)


class DeviceMaster(Base):
    __tablename__ = "device_table"
    id = Column(Integer, autoincrement=True, primary_key=True)
    vendor = Column(String, nullable=False)
    model = Column(String, nullable=False)

    def __init__(
        self,
        id,
        vendor,
        model,
    ):
        self.id = id
        self.vendor = vendor
        self.model = model

    def __repr__(self):
        return "<DeviceMaster('{self.id}', '{self.vendor}', '{self.model}',".format(self=self)


class RegionMaster(Base):
    __tablename__ = "region_table"
    id = Column(Integer, autoincrement=True, primary_key=True)
    region = Column(String, nullable=False)

    def __init__(
        self,
        id,
        region,
    ):
        self.id = id
        self.region = region

    def __repr__(self):
        return "<RegionMaster('{self.id}','{self.region}',)>".format(self=self)


class DeviceRole(Base):
    __tablename__ = "device_role"
    id = Column(Integer, autoincrement=True, primary_key=True)
    role = Column(String, nullable=False)

    def __init__(
        self,
        id,
        role,
    ):
        self.id = id
        self.role = role

    def __repr__(self):
        return "<DeviceRole('{self.id}','{self.role}',)>".format(self=self)


class OsState(Base):
    __tablename__ = "os_validity"
    id = Column(Integer, autoincrement=True, primary_key=True)
    validity_state = Column(String, nullable=False)

    def __init__(
        self,
        id,
        validity_state,
    ):
        self.id = id
        self.validity_state = validity_state

    def __repr__(self):
        return "<OsState('{self.id}','{self.validity_state}',)>".format(self=self)


class PackageType(Base):
    __tablename__ = "package_type_table"
    id = Column(Integer, autoincrement=True, primary_key=True)
    package_type = Column(String, nullable=False)

    def __init__(
        self,
        id,
        package_type,
    ):
        self.id = id
        self.package_type = package_type

    def __repr__(self):
        return "<PackageType('{self.id}','{self.package_type}',)>".format(self=self)


class FileType(Base):
    __tablename__ = "file_type_table"
    id = Column(Integer, autoincrement=True, primary_key=True)
    file_type = Column(String, nullable=False)

    def __init__(
        self,
        id,
        file_type,
    ):
        self.id = id
        self.file_type = file_type

    def __repr__(self):
        return "<FileType('{self.id}','{self.file_type}',)>".format(self=self)


class DeviceRegion(Base):
    __tablename__ = "device_region"
    id = Column(Integer, autoincrement=True, primary_key=True)
    region_id = Column(Integer, ForeignKey("region_table.id"), nullable=False)
    device_id = Column(Integer, ForeignKey("device_table.id"), nullable=False)

    def __init__(
        self,
        id,
        region_id,
        device_id,
    ):
        self.id = id
        self.region_id = region_id
        self.device_id = device_id

    def __repr__(self):
        return "<DeviceRegion('{self.id}', '{self.region_id}', '{self.device_id}',".format(self=self)


class PhaseUpgrade(Base):
    __tablename__ = "phase_upgrade"
    id = Column(Integer, autoincrement=True, primary_key=True)
    source_osv_dr_id = Column(Integer, ForeignKey("os_version_device_region.id"), nullable=False)
    target_osv_dr_id = Column(Integer, ForeignKey("os_version_device_region.os_version_id"), nullable=False)
    createdBy = Column(String(20), nullable=False)  # noqa:  N803
    modifiedBy = Column(String(20), nullable=False)  # noqa:  N803
    createdOn = Column(DateTime, nullable=False, default=datetime.datetime.utcnow())  # noqa:  N803
    modifiedOn = Column(DateTime, nullable=False, default=datetime.datetime.utcnow())  # noqa:  N803
    custom_config_id = Column(Integer, ForeignKey("custom_config_list.id"), nullable=False)

    def __init__(
        self,
        source_osv_dr_id: int,
        target_osv_dr_id: int,
        createdBy: str,  # noqa:  N803
        modifiedBy: str,
        custom_config_id: int,
        createdOn: str = datetime.datetime.now(datetime.timezone.utc),
        modifiedOn: str = datetime.datetime.now(datetime.timezone.utc),
    ) -> None:
        """
        Initializes an instance of software lifecycle model
        """
        self.source_osv_dr_id = source_osv_dr_id
        self.target_osv_dr_id = target_osv_dr_id
        self.createdBy = createdBy
        self.modifiedBy = modifiedBy
        self.createdOn = createdOn
        self.modifiedOn = modifiedOn
        self.custom_config_id = custom_config_id

    def __repr__(self) -> Query:
        return (
            "<PhaseUpgrade('{self.id}', '{self.source_osv_dr_id}', '{self.target_osv_dr_id}',"
            " '{self.createdBy}',"
            " '{self.modifiedBy}','{self.createdOn}' , '{self.modifiedOn}',"
            " '{self.custom_config_id}')>".format(self=self)
        )


class CustomConfigList(Base):
    __tablename__ = "custom_config_list"
    id = Column(Integer, autoincrement=True, primary_key=True)
    role_list_id = Column(Integer, ForeignKey("role_list.id"), nullable=False)
    pre_target_upgrade_conf = Column(String)
    post_target_upgrade_conf = Column(String)
    is_rollback_required = Column(Boolean)
    before_rollback = Column(String)
    after_rollback = Column(String)
    config_mode = Column(String)
    next_config_id = Column(Integer, ForeignKey("custom_config_list.id"), nullable=False)

    def __init__(
        self,
        role_list_id: int,
        pre_target_upgrade_conf: str,
        post_target_upgrade_conf: str,
        is_rollback_required: bool,
        before_rollback: str,
        after_rollback: str,
        config_mode: str,
        next_config_id: int,
    ) -> None:
        """
        Initializes an instance of software lifecycle model
        """
        self.role_list_id = role_list_id
        self.next_config_id = next_config_id
        self.pre_target_upgrade_conf = pre_target_upgrade_conf
        self.post_target_upgrade_conf = post_target_upgrade_conf
        self.is_rollback_required = is_rollback_required
        self.before_rollback = before_rollback
        self.after_rollback = after_rollback
        self.config_mode = config_mode

    def __repr__(self) -> Query:
        return (
            "<CustomConfigList('{self.id}', '{self.role_list_id}', '{self.next_config_id}',"
            " '{self.pre_target_upgrade_conf}', '{self.post_target_upgrade_conf}',"
            " '{self.is_rollback_required}', '{self.before_rollback}', '{self.after_rollback}'"
            " '{self.config_mode}')>".format(self=self)
        )


class RoleList(Base):
    __tablename__ = "role_list"
    id = Column(Integer, autoincrement=True, primary_key=True)
    role_id1 = Column(Integer, ForeignKey("device_role.id"))
    role_id2 = Column(Integer, ForeignKey("device_role.id"))
    role_id3 = Column(Integer, ForeignKey("device_role.id"))
    role_id4 = Column(Integer, ForeignKey("device_role.id"))
    role_id5 = Column(Integer, ForeignKey("device_role.id"))
    role_id6 = Column(Integer, ForeignKey("device_role.id"))
    role_id7 = Column(Integer, ForeignKey("device_role.id"))
    role_id8 = Column(Integer, ForeignKey("device_role.id"))
    role_id9 = Column(Integer, ForeignKey("device_role.id"))
    role_id10 = Column(Integer, ForeignKey("device_role.id"))
    role_id11 = Column(Integer, ForeignKey("device_role.id"))
    role_id12 = Column(Integer, ForeignKey("device_role.id"))
    role_id13 = Column(Integer, ForeignKey("device_role.id"))
    role_id14 = Column(Integer, ForeignKey("device_role.id"))
    role_id15 = Column(Integer, ForeignKey("device_role.id"))
    role_id16 = Column(Integer, ForeignKey("device_role.id"))
    role_id17 = Column(Integer, ForeignKey("device_role.id"))
    role_id18 = Column(Integer, ForeignKey("device_role.id"))
    role_id19 = Column(Integer, ForeignKey("device_role.id"))
    role_id20 = Column(Integer, ForeignKey("device_role.id"))
    role_id21 = Column(Integer, ForeignKey("device_role.id"))
    role_id22 = Column(Integer, ForeignKey("device_role.id"))
    role_id23 = Column(Integer, ForeignKey("device_role.id"))
    role_id24 = Column(Integer, ForeignKey("device_role.id"))
    role_id25 = Column(Integer, ForeignKey("device_role.id"))
    role_id26 = Column(Integer, ForeignKey("device_role.id"))
    role_id27 = Column(Integer, ForeignKey("device_role.id"))
    role_id28 = Column(Integer, ForeignKey("device_role.id"))
    role_id29 = Column(Integer, ForeignKey("device_role.id"))
    role_id30 = Column(Integer, ForeignKey("device_role.id"))
    role_id31 = Column(Integer, ForeignKey("device_role.id"))
    role_id32 = Column(Integer, ForeignKey("device_role.id"))
    role_id33 = Column(Integer, ForeignKey("device_role.id"))
    role_id34 = Column(Integer, ForeignKey("device_role.id"))
    role_id35 = Column(Integer, ForeignKey("device_role.id"))
    role_id36 = Column(Integer, ForeignKey("device_role.id"))
    role_id37 = Column(Integer, ForeignKey("device_role.id"))
    role_id38 = Column(Integer, ForeignKey("device_role.id"))

    def __init__(
        self,
        role_id1: int = None,
        role_id2: int = None,
        role_id3: int = None,
        role_id4: int = None,
        role_id5: int = None,
        role_id6: int = None,
        role_id7: int = None,
        role_id8: int = None,
        role_id9: int = None,
        role_id10: int = None,
        role_id11: int = None,
        role_id12: int = None,
        role_id13: int = None,
        role_id14: int = None,
        role_id15: int = None,
        role_id16: int = None,
        role_id17: int = None,
        role_id18: int = None,
        role_id19: int = None,
        role_id20: int = None,
        role_id21: int = None,
        role_id22: int = None,
        role_id23: int = None,
        role_id24: int = None,
        role_id25: int = None,
        role_id26: int = None,
        role_id27: int = None,
        role_id28: int = None,
        role_id29: int = None,
        role_id30: int = None,
        role_id31: int = None,
        role_id32: int = None,
        role_id33: int = None,
        role_id34: int = None,
        role_id35: int = None,
        role_id36: int = None,
        role_id37: int = None,
        role_id38: int = None,
    ) -> None:
        """
        Initializes an instance of software lifecycle model
        """
        self.role_id1 = role_id1
        self.role_id2 = role_id2
        self.role_id3 = role_id3
        self.role_id4 = role_id4
        self.role_id5 = role_id5
        self.role_id6 = role_id6
        self.role_id7 = role_id7
        self.role_id8 = role_id8
        self.role_id9 = role_id9
        self.role_id10 = role_id10
        self.role_id11 = role_id11
        self.role_id12 = role_id12
        self.role_id13 = role_id13
        self.role_id14 = role_id14
        self.role_id15 = role_id15
        self.role_id16 = role_id16
        self.role_id17 = role_id17
        self.role_id18 = role_id18
        self.role_id19 = role_id19
        self.role_id20 = role_id20
        self.role_id21 = role_id21
        self.role_id22 = role_id22
        self.role_id23 = role_id23
        self.role_id24 = role_id24
        self.role_id25 = role_id25
        self.role_id26 = role_id26
        self.role_id27 = role_id27
        self.role_id28 = role_id28
        self.role_id29 = role_id29
        self.role_id30 = role_id30
        self.role_id31 = role_id31
        self.role_id32 = role_id32
        self.role_id33 = role_id33
        self.role_id34 = role_id34
        self.role_id35 = role_id35
        self.role_id36 = role_id36
        self.role_id37 = role_id37
        self.role_id38 = role_id38

    def __repr__(self) -> Query:
        return (
            "<RoleList('{self.id}', '{self.role_id1}', '{self.role_id2}', '{self.role_id3}',"
            " '{self.role_id4}', '{self.role_id5}', '{self.role_id6}', '{self.role_id7}',"
            " '{self.role_id8}', '{self.role_id9}', '{self.role_id10}', '{self.role_id11}',"
            " '{self.role_id12}', '{self.role_id13}', '{self.role_id14}', '{self.role_id15}',"
            " '{self.role_id16}', '{self.role_id17}', '{self.role_id18}', '{self.role_id19}',"
            " '{self.role_id20}', '{self.role_id21}', '{self.role_id22}', '{self.role_id23}',"
            " '{self.role_id24}', '{self.role_id25}', '{self.role_id26}', '{self.role_id27}',"
            " '{self.role_id28}', '{self.role_id29}', '{self.role_id30}', '{self.role_id31}',"
            " '{self.role_id32}', '{self.role_id33}', '{self.role_id34}', '{self.role_id35}',"
            " '{self.role_id36}', '{self.role_id37}', '{self.role_id38}')>".format(self=self)
        )


class SequenceUpgrade(Base):
    __tablename__ = "sequence_upgrade"
    id = Column(Integer, autoincrement=True, primary_key=True)
    steps = Column(Integer, nullable=False)
    sequence_no = Column(Integer, nullable=False)
    comments = Column(String, nullable=True)
    next_sequence_id = Column(Integer, ForeignKey("sequence_upgrade.id"))
    phase_upgrade_id = Column(Integer, ForeignKey("phase_upgrade.id"), nullable=False)
    deviceregion_id = Column(Integer, ForeignKey("device_region.id"), nullable=False)
    createdBy = Column(String(20), nullable=False)  # noqa:  N803
    modifiedBy = Column(String(20), nullable=False)  # noqa:  N803
    createdOn = Column(DateTime, default=datetime.datetime.utcnow())  # noqa:  N803
    modifiedOn = Column(DateTime, default=datetime.datetime.utcnow())  # noqa:  N803

    def __init__(
        self,
        steps,
        sequence_no,
        comments,
        next_sequence_id,
        phase_upgrade_id,
        deviceregion_id,
        createdBy,  # noqa:  N803
        modifiedBy,
        createdOn=datetime.datetime.utcnow(),
        modifiedOn=datetime.datetime.utcnow(),
    ):
        self.steps = steps
        self.sequence_no = sequence_no
        self.comments = comments
        self.next_sequence_id = next_sequence_id
        self.phase_upgrade_id = phase_upgrade_id
        self.deviceregion_id = deviceregion_id
        self.createdBy = createdBy
        self.modifiedBy = modifiedBy
        self.createdOn = createdOn
        self.modifiedOn = modifiedOn

    def __repr__(self):
        return (
            "<SequenceUpgrade('{self.id}', '{self.steps}', '{self.sequence_no}', '{self.comments}',"
            "  '{self.next_sequence_id}', '{self.phase_upgrade_id}', '{self.deviceregion_id}', '{self.createdBy}',"
            " '{self.modifiedBy}','{self.createdOn}' , '{self.modifiedOn}')>".format(self=self)
        )


class Image(Base):
    __tablename__ = "image"
    id = Column(Integer, autoincrement=True, primary_key=True)
    url = Column(String(100), nullable=False)
    md5 = Column(String(128), nullable=False)
    file_type = Column(Integer, ForeignKey("file_type_table.id"), nullable=False)
    file_size = Column(String(1264), nullable=False)
    comments = Column(String, nullable=True)
    os_version_id = Column(Integer, ForeignKey("os_version.id"), nullable=False)
    os_device_region_id = Column(Integer, ForeignKey("os_version_device_region.id"), nullable=False)
    createdBy = Column(String(20), nullable=False)  # noqa:  N803
    modifiedBy = Column(String(20), nullable=False)  # noqa:  N803
    createdOn = Column(DateTime, default=datetime.datetime.utcnow())  # noqa:  N803
    modifiedOn = Column(DateTime, default=datetime.datetime.utcnow())  # noqa:  N803

    def __init__(
        self,
        url,
        md5,
        file_type,
        file_size,
        comments,
        os_version_id,
        os_device_region_id,
        createdBy,  # noqa:  N803
        modifiedBy,
        createdOn=datetime.datetime.now(datetime.timezone.utc),
        modifiedOn=datetime.datetime.now(datetime.timezone.utc),
    ):
        self.url = url
        self.file_type = file_type
        self.file_size = file_size
        self.comments = comments
        self.md5 = md5
        self.os_version_id = os_version_id
        self.os_device_region_id = os_device_region_id
        self.createdBy = createdBy
        self.modifiedBy = modifiedBy
        self.createdOn = createdOn
        self.modifiedOn = modifiedOn

    def __repr__(self):
        return (
            "<Image('{self.id}', '{self.file_type}', '{self.file_size}', '{self.comments}', '{self.md5}',"
            " '{self.os_version_id}', '{self.os_device_region_id}'"
            "'{self.createdBy}', '{self.modifiedBy}','{self.createdOn}' , '{self.modifiedOn}')>".format(self=self)
        )


class Package(Base):
    __tablename__ = "package_table"
    id = Column(Integer, autoincrement=True, primary_key=True)
    package_type = Column(Integer, ForeignKey("package_type_table.id"), nullable=False)
    package_name = Column(String(256), nullable=False)
    image_id = Column(Integer, ForeignKey("os_version.id"), nullable=False)
    createdBy = Column(String(20), nullable=False)  # noqa:  N803
    modifiedBy = Column(String(20), nullable=False)  # noqa:  N803
    createdOn = Column(DateTime, default=datetime.datetime.utcnow())  # noqa:  N803
    modifiedOn = Column(DateTime, default=datetime.datetime.utcnow())  # noqa:  N803

    def __init__(
        self,
        package_type,
        package_name,
        image_id,
        createdBy,  # noqa:  N803
        modifiedBy,
        createdOn=datetime.datetime.utcnow(),
        modifiedOn=datetime.datetime.utcnow(),
    ):
        self.package_type = package_type
        self.package_name = package_name
        self.image_id = image_id
        self.createdBy = createdBy
        self.modifiedBy = modifiedBy
        self.createdOn = createdOn
        self.modifiedOn = modifiedOn

    def __repr__(self):
        return (
            "<Package('{self.id}', '{self.package_type}', '{self.package_name}', '{self.image_id}',"
            "'{self.createdBy}', '{self.modifiedBy}','{self.createdOn}' , '{self.modifiedOn}')>".format(self=self)
        )


class OSVersion(Base):
    __tablename__ = "os_version"
    id = Column(Integer, autoincrement=True, primary_key=True)
    os = Column(String(100), nullable=False)
    os_version = Column(String(100), nullable=False)
    os_label = Column(String(100), nullable=False)
    createdBy = Column(String(20), nullable=False)  # noqa:  N803
    modifiedBy = Column(String(20), nullable=False)  # noqa:  N803
    createdOn = Column(DateTime, default=datetime.datetime.utcnow())  # noqa:  N803
    modifiedOn = Column(DateTime, default=datetime.datetime.utcnow())  # noqa:  N803

    def __init__(
        self,
        os,
        os_version,
        os_label,
        createdBy,  # noqa:  N803
        modifiedBy,
        createdOn=datetime.datetime.utcnow(),
        modifiedOn=datetime.datetime.utcnow(),
    ):
        self.os = os
        self.os_version = os_version
        self.os_label = (os_label,)
        self.createdBy = createdBy
        self.modifiedBy = modifiedBy
        self.createdOn = createdOn
        self.modifiedOn = modifiedOn

    def __repr__(self):
        return (
            "<OSVersion('{self.id}', '{self.os}', '{self.os_version}', '{self.os_label}', '{self.createdBy}',"
            " '{self.Status}','{self.modifiedBy}','{self.createdOn}' , '{self.modifiedOn}')>".format(self=self)
        )


class OSVersionDeviceRegionPackage(Base):
    __tablename__ = "os_version_device_region"
    id = Column(Integer, autoincrement=True, primary_key=True)
    device_region_id = Column(Integer, ForeignKey("device_region.id"), nullable=False)
    os_version_id = Column(Integer, ForeignKey("os_version.id"), nullable=False)
    os_validity_id = Column(Integer, ForeignKey("os_validity.id"), nullable=False)
    createdBy = Column(String(20), nullable=False)  # noqa:  N803
    modifiedBy = Column(String(20), nullable=False)  # noqa:  N803
    createdOn = Column(DateTime, default=datetime.datetime.utcnow())  # noqa:  N803
    modifiedOn = Column(DateTime, default=datetime.datetime.utcnow())  # noqa:  N803

    def __init__(
        self,
        device_region_id,
        os_version_id,
        os_validity_id,
        createdBy,  # noqa:  N803
        modifiedBy,
        createdOn=datetime.datetime.utcnow(),
        modifiedOn=datetime.datetime.utcnow(),
    ):
        self.device_region_id = device_region_id
        self.os_version_id = os_version_id
        self.os_validity_id = os_validity_id
        self.createdBy = createdBy
        self.modifiedBy = modifiedBy
        self.createdOn = createdOn
        self.modifiedOn = modifiedOn

    def __repr__(self):
        return (
            "<OSVersionDeviceRegionPackage('{self.id}', '{self.device_region_id}',"
            " '{self.os_version_id}', '{self.os_validity_id}', '{self.createdBy}',"
            " '{self.Status}','{self.modifiedBy}','{self.createdOn}' , '{self.modifiedOn}')>".format(self=self)
        )


class TrafficProtocol(Base):
    __tablename__ = "traffic_protocol"

    id = Column(Integer, autoincrement=True, primary_key=True)
    protocol = Column(String, nullable=False)
    createdBy = Column(String(20), nullable=False)  # noqa:  N803
    modifiedBy = Column(String(20), nullable=False)  # noqa:  N803
    createdOn = Column(DateTime, default=datetime.datetime.utcnow())  # noqa:  N803
    modifiedOn = Column(DateTime, default=datetime.datetime.utcnow())  # noqa:  N803

    def __init__(
        self,
        id,
        protocol,
        createdBy,  # noqa:  N803
        modifiedBy,
        createdOn=datetime.datetime.utcnow(),
        modifiedOn=datetime.datetime.utcnow(),
    ):
        self.id = id
        self.protocol = protocol
        self.createdBy = createdBy
        self.modifiedBy = modifiedBy
        self.createdOn = createdOn
        self.modifiedOn = modifiedOn

    def __repr__(self):
        return (
            "<TrafficProtocol('{self.id}', '{self.protocol}',"
            " '{self.createdBy}',"
            " '{self.modifiedBy}', '{self.createdOn}', '{self.modifiedOn}')>".format(self=self)
        )


class TrafficDiversion(Base):
    __tablename__ = "traffic_diversion"

    id = Column(Integer, autoincrement=True, primary_key=True)
    protocol_step = Column(Integer, ForeignKey("traffic_protocol.id"), nullable=False)
    device_region_id = Column(Integer, ForeignKey("device_region.id"), nullable=False)
    device_role_id = Column(Integer, ForeignKey("device_role.id"), nullable=False)
    traffic_type = Column(String, nullable=False)
    exclusion = Column(String, nullable=False)
    sequence = Column(Integer, nullable=False)
    wait_time = Column(Integer, nullable=False)

    def __init__(
        self,
        id,
        protocol_step,
        device_region_id,
        device_role_id,
        traffic_type,
        exclusion,
        sequence,
        wait_time,
    ):
        self.id = id
        self.protocol_step = protocol_step
        self.device_region_id = device_region_id
        self.device_role_id = device_role_id
        self.traffic_type = traffic_type
        self.exclusion = exclusion
        self.sequence = sequence
        self.wait_time = wait_time

    def __repr__(self):
        return (
            "<TrafficDiversion('{self.id}', '{self.device_region_id}',"
            " '{self.protocol_step}', '{self.device_role_id}', '{self.traffic_type}',"
            " '{self.exclusion}','{self.sequence}','{self.wait_time}')>".format(self=self)
        )


class ServiceCheck(Base):
    __tablename__ = "service_check"

    id = Column(Integer, autoincrement=True, primary_key=True)
    device_region_id = Column(Integer, ForeignKey("device_region.id"), nullable=False)
    device_role_id = Column(Integer, ForeignKey("device_role.id"), nullable=False)
    is_service_required = Column(Boolean, nullable=False)

    def __init__(
        self,
        id,
        device_region_id,
        device_role_id,
        is_service_required,
    ):
        self.id = id
        self.device_region_id = device_region_id
        self.device_role_id = device_role_id
        self.is_service_required = is_service_required

    def __repr__(self):
        return (
            "<ServiceCheck('{self.id}', '{self.device_region_id}',"
            "'{self.device_role_id}', '{self.is_service_required}')>".format(self=self)
        )
