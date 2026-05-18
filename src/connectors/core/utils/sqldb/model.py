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
from sqlalchemy import Column, DateTime, ForeignKey, Integer, MetaData, String
from sqlalchemy.ext.declarative import declarative_base

metadata = MetaData()

Base = declarative_base(metadata=metadata)


class DeviceMaster(Base):
    __tablename__ = "DeviceMaster"
    DeviceIdentifier = Column(Integer, autoincrement=True, primary_key=True)
    DeviceVendor = Column(String, nullable=False)
    DeviceRole = Column(String, nullable=False)
    DeviceModel = Column(String, nullable=False)
    CreatedBy = Column(String(20), nullable=False)
    ModifiedBy = Column(String(20))
    CreatedOn = Column(DateTime, default=datetime.datetime.utcnow())
    ModifiedOn = Column(DateTime, default=datetime.datetime.utcnow())

    def __init__(
        self,
        DeviceVendor,  # noqa:  N803
        DeviceRole,
        DeviceModel,
        CreatedBy,
        ModifiedBy=None,  # noqa:  N803
        CreatedOn=datetime.datetime.utcnow(),
        ModifiedOn=datetime.datetime.utcnow(),
    ):  # noqa:  N803
        self.DeviceVendor = DeviceVendor
        self.DeviceRole = DeviceRole
        self.DeviceModel = DeviceModel
        self.CreatedBy = CreatedBy
        self.ModifiedBy = ModifiedBy
        self.CreatedOn = CreatedOn
        self.ModifiedOn = ModifiedOn

    def __repr__(self):
        return (
            "<DeviceMaster('{self.DeviceVendor}', '{self.DeviceRole}','{self.DeviceModel}',"
            " '{self.CreatedBy}', '{self.ModifiedBy}', '{self.CreatedOn}' , '{self.ModifiedOn}')>".format(self=self)
        )


class OSVersionMaster(Base):
    __tablename__ = "OSVersionMaster"
    OSVersionIdentifier = Column(Integer, autoincrement=True, primary_key=True)
    OS = Column(String, nullable=False)
    OSVersion = Column(String, nullable=False)
    CreatedBy = Column(String(20), nullable=False)
    ModifiedBy = Column(String(20))
    CreatedOn = Column(DateTime, default=datetime.datetime.utcnow())
    ModifiedOn = Column(DateTime, default=datetime.datetime.utcnow())

    def __init__(
        self,
        OS,  # noqa:  N803
        OSVersion,
        CreatedBy,
        ModifiedBy=None,  # noqa:  N803
        CreatedOn=datetime.datetime.utcnow(),  # noqa:  N803
        ModifiedOn=datetime.datetime.utcnow(),
    ):  # noqa:  N803
        self.OS = OS
        self.OSVersion = OSVersion
        self.CreatedBy = CreatedBy
        self.ModifiedBy = ModifiedBy
        self.CreatedOn = CreatedOn
        self.ModifiedOn = ModifiedOn

    def __repr__(self):
        return (
            "<OSVersionMaster('{self.OS}', '{self.OSVersion}','{self.CreatedBy}', '{self.ModifiedBy}', "
            "'{self.CreatedOn}' , '{self.ModifiedOn}')>".format(self=self)
        )


class DeviceOSVersion(Base):
    __tablename__ = "DeviceOSVersion"
    DeviceOSVersionIdentifier = Column(Integer, autoincrement=True, primary_key=True)
    DeviceIdentifier = Column(Integer, ForeignKey("DeviceMaster.DeviceIdentifier"), nullable=False)
    OSVersionIdentifier = Column(Integer, ForeignKey("OSVersionMaster.OSVersionIdentifier"), nullable=False)
    Status = Column(String, nullable=False)
    CreatedBy = Column(String(20), nullable=False)
    ModifiedBy = Column(String(20))
    CreatedOn = Column(DateTime, default=datetime.datetime.utcnow())
    ModifiedOn = Column(DateTime, default=datetime.datetime.utcnow())

    def __init__(
        self,
        DeviceIdentifier,  # noqa:  N803
        OSVersionIdentifier,
        CreatedBy,
        Status="Inactive",  # noqa:  N803
        ModifiedBy=None,
        CreatedOn=datetime.datetime.utcnow(),  # noqa:  N803
        ModifiedOn=datetime.datetime.utcnow(),
    ):  # noqa:  N803
        self.DeviceIdentifier = DeviceIdentifier
        self.OSVersionIdentifier = OSVersionIdentifier
        self.Status = Status
        self.CreatedBy = CreatedBy
        self.ModifiedBy = ModifiedBy
        self.CreatedOn = CreatedOn
        self.ModifiedOn = ModifiedOn

    def __repr__(self):
        return (
            "<DeviceOSVersion('{self.DeviceIdentifier}', '{self.OSVersionIdentifier}','{self.CreatedBy}',"
            " '{self.Status}','{self.ModifiedBy}','{self.CreatedOn}' , '{self.ModifiedOn}')>".format(self=self)
        )


class BootableFileDetails(Base):
    __tablename__ = "BootableFileDetails"
    FileIdentifier = Column(Integer, autoincrement=True, primary_key=True)
    FileName = Column(String(100), nullable=False)
    MD5Checksum = Column(String(128), nullable=False)
    DeviceOSVersionIdentifier = Column(Integer, ForeignKey("DeviceOSVersion.DeviceOSVersionIdentifier"), nullable=False)
    CreatedBy = Column(String(20), nullable=False)
    ModifiedBy = Column(String(20))
    CreatedOn = Column(DateTime, default=datetime.datetime.utcnow())
    ModifiedOn = Column(DateTime, default=datetime.datetime.utcnow())

    def __init__(
        self,
        FileName,  # noqa:  N803
        MD5Checksum,
        DeviceOSVersionIdentifier,
        CreatedBy,  # noqa:  N803
        ModifiedBy=None,
        CreatedOn=datetime.datetime.utcnow(),  # noqa:  N803
        ModifiedOn=datetime.datetime.utcnow(),
    ):  # noqa:  N803
        self.FileName = FileName
        self.MD5Checksum = MD5Checksum
        self.DeviceOSVersionIdentifier = DeviceOSVersionIdentifier
        self.CreatedBy = CreatedBy
        self.ModifiedBy = ModifiedBy
        self.CreatedOn = CreatedOn
        self.ModifiedOn = ModifiedOn

    def __repr__(self):
        return (
            "<BootableFileDetails('{self.FileName}', '{self.MD5Checksum}', '{self.DeviceOSVersionIdentifier}',"
            "'{self.CreatedBy}', '{self.ModifiedBy}','{self.CreatedOn}' , '{self.ModifiedOn}')>".format(self=self)
        )


class RPMPackageDetails(Base):
    __tablename__ = "RPMPackageDetails"
    PackageIdentifier = Column(Integer, autoincrement=True, primary_key=True)
    FileType = Column(String, nullable=False)
    FileName = Column(String(100), nullable=False)
    DeviceOSVersionIdentifier = Column(Integer, ForeignKey("DeviceOSVersion.DeviceOSVersionIdentifier"), nullable=False)
    CreatedBy = Column(String(20), nullable=False)
    ModifiedBy = Column(String(20))
    CreatedOn = Column(DateTime, default=datetime.datetime.utcnow())
    ModifiedOn = Column(DateTime, default=datetime.datetime.utcnow())

    def __init__(
        self,
        FileType,  # noqa:  N803
        FileName,
        DeviceOSVersionIdentifier,
        CreatedBy,  # noqa:  N803
        ModifiedBy=None,
        CreatedOn=datetime.datetime.utcnow(),  # noqa:  N803
        ModifiedOn=datetime.datetime.utcnow(),
    ):  # noqa:  N803
        self.FileType = FileType
        self.FileName = FileName
        self.DeviceOSVersionIdentifier = DeviceOSVersionIdentifier
        self.CreatedBy = CreatedBy
        self.ModifiedBy = ModifiedBy
        self.CreatedOn = CreatedOn
        self.ModifiedOn = ModifiedOn

    def __repr__(self):
        return (
            "<RPMPackageDetails('{self.FileType}', '{self.FileName}', '{self.DeviceOSVersionIdentifier}',"
            "'{self.CreatedBy}', '{self.ModifiedBy}','{self.CreatedOn}' , '{self.ModifiedOn}')>".format(self=self)
        )


class CiscoTokens(Base):
    __tablename__ = "CiscoTokens"
    TokenId = Column(Integer, autoincrement=True, primary_key=True)
    Token = Column(String(255), nullable=False)
    Description = Column(String(255))
    ExpiryDate = Column(DateTime, nullable=False)
    ExportControl = Column(String(255), nullable=False)
    CreatedBy = Column(String(20), nullable=False)
    CreatedDate = Column(DateTime, default=datetime.datetime.utcnow())

    def __init__(
        self,
        Token,  # noqa:  N803
        ExpiryDate,
        ExportControl,
        CreatedBy,
        Description=None,  # noqa:  N803
        CreatedDate=datetime.datetime.utcnow(),
    ):  # noqa:  N803
        self.Token = Token
        self.ExpiryDate = ExpiryDate
        self.ExportControl = ExportControl
        self.CreatedBy = CreatedBy
        self.Description = Description
        self.CreatedDate = CreatedDate

    def __repr__(self):
        return (
            "<CiscoTokens('{self.Token}', '{self.ExpiryDate}', '{self.ExportControl}','{self.CreatedBy}', "
            "'{self.Description}','{self.CreatedDate}')>".format(self=self)
        )


class DeviceCommands(Base):
    __tablename__ = "Device_Commands"
    DeviceCommandId = Column(Integer, autoincrement=True, primary_key=True)
    DeviceId = Column(Integer, nullable=False)
    CmdId = Column(Integer, nullable=False)

    def __init__(self, DeviceId, CmdId):  # noqa:  N803
        self.DeviceId = DeviceId
        self.CmdId = CmdId

    def __repr__(self):
        return "<Device_Commands('{self.DeviceId}', '{self.CmdId}')>".format(self=self)


class Commands(Base):
    __tablename__ = "Commands"
    CmdId = Column(Integer, autoincrement=True, nullable=False, primary_key=True)
    Command = Column(String(255), nullable=False)

    def __init__(self, CmdId, Command):  # noqa:  N803
        self.CmdId = CmdId
        self.Command = Command

    def __repr__(self):
        return "<Commands('{self.CmdId}','{self.Command}')>".format(self=self)


class Devices(Base):
    __tablename__ = "Devices"
    DeviceId = Column(Integer, autoincrement=True, nullable=False, primary_key=True)
    Vendor = Column(String(255), nullable=False)
    Model = Column(String(255), nullable=False)
    Platform = Column(String(255), nullable=False)
    Version = Column(String(255), nullable=False)

    def __init__(self, DeviceId, Vendor, Model, Platform, Version):  # noqa:  N803
        self.DeviceId = DeviceId
        self.Vendor = Vendor
        self.Model = Model
        self.Platform = Platform
        self.Version = Version

    def __repr__(self):
        return "<Devices('{self.DeviceId}','{self.Vendor}'," "{self.Model}','{self.Platform}',{self.Version}')>".format(
            self=self
        )


class SkybridgeTransactions(Base):
    __tablename__ = "skybridge_transactions"
    id = Column(Integer, primary_key=True)
    username = Column(String(255), nullable=False)
    target_router = Column(String(255), nullable=False)
    device_vendor = Column(String(255), nullable=False)
    device_os_type = Column(String(255), nullable=False)
    device_os_version = Column(String(255), nullable=False)
    device_model = Column(String(255), nullable=False)
    origin = Column(String(255), nullable=False)
    transaction_start = Column(String(255), nullable=False)
    transaction_end = Column(String(255), nullable=False)
    command = Column(String(500), nullable=False)
    exception = Column(String(255), nullable=False)
    x_request_id = Column(String(255), nullable=True)
    output = Column(String(2000), nullable=True)
    timestamp = Column(String(255), nullable=False)

    def __init__(
        self,
        id,
        username,
        target_router,
        device_vendor,
        device_os_type,
        device_os_version,
        device_model,
        origin,
        transaction_start,
        transaction_end,
        command,
        exception,
        x_request_id,
        output,
        timestamp,
    ):  # noqa:  N803
        self.id = id
        self.username = username
        self.target_router = target_router
        self.device_vendor = device_vendor
        self.device_os_type = device_os_type
        self.device_os_version = device_os_version
        self.device_model = device_model
        self.origin = origin
        self.transaction_start = transaction_start
        self.transaction_end = transaction_end
        self.command = command
        self.exception = exception
        self.x_request_id = x_request_id
        self.output = output
        self.timestamp = timestamp

    def __repr__(self):
        return (
            "<skybridge_transactions('{self.id}','{self.username}','{self.target_router}','{self.device_vendor}',"
            "'{self.device_os_type}','{self.device_os_version}','{self.device_model}','{self.origin}',"
            "'{self.transaction_start}','{self.transaction_end}','{self.command}','{self.exception}',"
            "'{self.x_request_id}','{self.output}','{self.timestamp}')>".format(self=self)
        )


class SkybridgeCommands(Base):
    __tablename__ = "skybridge_commands"
    id = Column(Integer, primary_key=True)
    username = Column(String(255), nullable=False)
    target_router = Column(String(255), nullable=False)
    device_vendor = Column(String(255), nullable=False)
    device_os_type = Column(String(255), nullable=False)
    device_os_version = Column(String(255), nullable=False)
    device_model = Column(String(255), nullable=False)
    command = Column(String(500), nullable=False)
    output = Column(String(2000), nullable=True)
    count = Column(Integer, nullable=False)

    def __init__(
        self,
        id,
        username,
        target_router,
        device_vendor,
        device_os_type,
        device_os_version,
        device_model,
        command,
        output,
        count,
    ):  # noqa:  N803
        self.id = id
        self.username = username
        self.target_router = target_router
        self.device_vendor = device_vendor
        self.device_os_type = device_os_type
        self.device_os_version = device_os_version
        self.device_model = device_model
        self.command = command
        self.output = output
        self.count = count

    def __repr__(self):
        return (
            "<skybridge_commands('{self.id}','{self.username}','{self.target_router}','{self.device_vendor}',"
            "'{self.device_os_type}','{self.device_os_version}','{self.device_model}',"
            "'{self.command}','{self.output}','{self.count}')>".format(self=self)
        )


class Tokens(Base):
    __tablename__ = "Tokens"
    id = Column(Integer, primary_key=True)
    system = Column(String(100), nullable=False)
    token = Column(String(2000), nullable=False)
    created_at = Column(DateTime, nullable=False)
    expiry_at = Column(DateTime, nullable=False)
    comment = Column(String(2000))

    def __init__(
        self,
        id,
        system,
        token,
        created_at,
        expiry_at,
        comment,
    ):
        self.id = id
        self.system = system
        self.token = token
        self.created_at = created_at
        self.expiry_at = expiry_at
        self.comment = comment

    def __repr__(self):
        return (
            "<tokens('{self.id}','{self.system}','{self.token}','{self.created_at}','{self.expiry_at}',"
            "'{self.comment}')>".format(self=self)
        )
