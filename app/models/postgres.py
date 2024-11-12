from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, Boolean, SmallInteger, Date, TEXT
from sqlalchemy.schema import ForeignKey
from sqlalchemy.orm import declarative_base

current_year =  datetime.now().year
Base = declarative_base()

class UniqueOrgTitles(Base):
	__tablename__ = 'UniqueOrgTitles'
	id = Column(BigInteger(), primary_key=True)
	org_title = Column(TEXT())

class UniqueMitTitles(Base):
    __tablename__ = 'UniqueMitTitles'
    id = Column(BigInteger(), primary_key=True)
    mit_title = Column(TEXT())

class UniqueMitNumbers(Base):
	__tablename__ = 'UniqueMitNumbers'
	id = Column(BigInteger(), primary_key=True)
	mit_number = Column(TEXT())

class UniqueMitNotations(Base):
    __tablename__ = 'UniqueMitNotations'
    id = Column(BigInteger(), primary_key=True)
    mit_notation = Column(TEXT())
     
class UniqueMiModifications(Base):
    __tablename__ = 'UniqueMiModifications'
    id = Column(BigInteger(), primary_key=True)
    mi_modification = Column(TEXT())

class EquipmentInfo(Base):
    __tablename__ = 'EquipmentInfo'
    id = Column(BigInteger(), primary_key=True)
    mi_number = Column(TEXT())
    result_docnum = Column(TEXT())
    verification_date = Column(Date())
    valid_date = Column(Date())
    vri_id = Column(BigInteger())
    applicability = Column(Boolean())
    org_titleId = Column(Integer(), ForeignKey('UniqueOrgTitles.id'))
    mit_titleId = Column(Integer(), ForeignKey('UniqueMitTitles.id'))
    mit_numberId = Column(Integer(), ForeignKey('UniqueMitNumbers.id'))
    mit_notationId = Column(Integer(), ForeignKey('UniqueMitNotations.id'))
    mi_modificationId = Column(Integer(), ForeignKey('UniqueMiModifications.id'))
    year = Column(SmallInteger())