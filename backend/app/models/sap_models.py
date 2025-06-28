from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ItemSTLBase(BaseModel):
    Code: str
    Name: str
    ForeignName: Optional[str] = None
    ItemsGroupCode: Optional[int] = None
    CustomsGroupCode: Optional[int] = None
    SalesVATGroup: Optional[str] = None
    BarCode: Optional[str] = None
    VatLiable: Optional[str] = None
    PurchaseItem: Optional[str] = None
    SalesItem: Optional[str] = None
    InventoryItem: Optional[str] = None
    IncomeAccount: Optional[str] = None
    ExemptIncomeAccount: Optional[str] = None
    ExpanseAccount: Optional[str] = None
    Mainsupplier: Optional[str] = None
    SupplierCatalogNo: Optional[str] = None
    DesiredInventory: Optional[float] = None
    MinInventory: Optional[float] = None
    Picture: Optional[str] = None
    User_Text: Optional[str] = None
    SerialNum: Optional[str] = None
    CommissionPercent: Optional[float] = None
    CommissionSum: Optional[float] = None
    CommissionGroup: Optional[int] = None
    TreeType: Optional[str] = None
    AssetItem: Optional[str] = None
    DataExportCode: Optional[str] = None
    Manufacturer: Optional[int] = None
    QuantityOnStock: Optional[float] = None
    QuantityOrderedFromVendors: Optional[float] = None
    QuantityOrderedByCustomers: Optional[float] = None
    ManageSerialNumbers: Optional[str] = None
    ManageBatchNumbers: Optional[str] = None
    Valid: Optional[str] = None
    ValidFrom: Optional[datetime] = None
    ValidTo: Optional[datetime] = None
    ValidRemarks: Optional[str] = None
    Frozen: Optional[str] = None
    FrozenFrom: Optional[datetime] = None
    FrozenTo: Optional[datetime] = None
    FrozenRemarks: Optional[str] = None
    SalesUnit: Optional[str] = None
    SalesItemsPerUnit: Optional[float] = None
    SalesPackagingUnit: Optional[str] = None
    SalesQtyPerPackUnit: Optional[float] = None
    SalesUnitLength: Optional[float] = None
    SalesLengthUnit: Optional[int] = None
    SalesUnitWidth: Optional[float] = None
    SalesWidthUnit: Optional[int] = None
    SalesUnitHeight: Optional[float] = None
    SalesHeightUnit: Optional[int] = None
    SalesUnitVolume: Optional[float] = None
    SalesVolumeUnit: Optional[int] = None
    SalesUnitWeight: Optional[float] = None
    SalesWeightUnit: Optional[int] = None
    PurchaseUnit: Optional[str] = None
    PurchaseItemsPerUnit: Optional[float] = None
    PurchasePackagingUnit: Optional[str] = None
    PurchaseQtyPerPackUnit: Optional[float] = None
    PurchaseUnitLength: Optional[float] = None
    PurchaseLengthUnit: Optional[int] = None
    PurchaseUnitWidth: Optional[float] = None
    PurchaseWidthUnit: Optional[int] = None
    PurchaseUnitHeight: Optional[float] = None
    PurchaseHeightUnit: Optional[int] = None
    PurchaseUnitVolume: Optional[float] = None
    PurchaseVolumeUnit: Optional[int] = None
    PurchaseUnitWeight: Optional[float] = None
    PurchaseWeightUnit: Optional[int] = None
    InventoryUnit: Optional[str] = None
    InventoryItemsPerUnit: Optional[float] = None
    InventoryPackagingUnit: Optional[str] = None
    InventoryQtyPerPackUnit: Optional[float] = None
    InventoryUnitLength: Optional[float] = None
    InventoryLengthUnit: Optional[int] = None
    InventoryUnitWidth: Optional[float] = None
    InventoryWidthUnit: Optional[int] = None
    InventoryUnitHeight: Optional[float] = None
    InventoryHeightUnit: Optional[int] = None
    InventoryUnitVolume: Optional[float] = None
    InventoryVolumeUnit: Optional[int] = None
    InventoryUnitWeight: Optional[float] = None
    InventoryWeightUnit: Optional[int] = None
    PortionItem: Optional[int] = None
    PortionWeight: Optional[float] = None
    LastPurchasePrice: Optional[float] = None
    LastPurchaseDate: Optional[datetime] = None
    LastPurchaseCurrency: Optional[str] = None
    AvgStdPrice: Optional[float] = None
    DefaultWarehouse: Optional[str] = None
    ShipType: Optional[int] = None
    GLMethod: Optional[str] = None
    TaxType: Optional[str] = None
    MaxInventory: Optional[float] = None
    ManageStockByWarehouse: Optional[str] = None
    PurchaseHeightUnit1: Optional[int] = None
    PurchaseUnitHeight1: Optional[float] = None
    PurchaseLengthUnit1: Optional[int] = None
    PurchaseUnitLength1: Optional[float] = None
    PurchaseWeightUnit1: Optional[int] = None
    PurchaseUnitWeight1: Optional[float] = None
    PurchaseWidthUnit1: Optional[int] = None
    PurchaseUnitWidth1: Optional[float] = None
    SalesHeightUnit1: Optional[int] = None
    SalesUnitHeight1: Optional[float] = None
    SalesLengthUnit1: Optional[int] = None
    SalesUnitLength1: Optional[float] = None
    SalesWeightUnit1: Optional[int] = None
    SalesUnitWeight1: Optional[float] = None
    SalesWidthUnit1: Optional[int] = None
    SalesUnitWidth1: Optional[float] = None
    ForceSelectionOfSerialNumber: Optional[str] = None
    ManageSerialNumbersOnReleaseOnly: Optional[str] = None
    WTLiable: Optional[str] = None
    CostAccountingMethod: Optional[str] = None
    SWW: Optional[str] = None
    WarrantyTemplate: Optional[str] = None
    IndirectTax: Optional[str] = None
    ArTaxCode: Optional[str] = None
    ApTaxCode: Optional[str] = None
    BaseUnitName: Optional[str] = None
    ItemCountryOrg: Optional[str] = None
    IssueMethod: Optional[str] = None
    SRIAndBatchManageMethod: Optional[str] = None
    IsPhantom: Optional[str] = None
    InventoryUOM: Optional[str] = None
    PlanningSystem: Optional[str] = None
    ProcurementMethod: Optional[str] = None
    ComponentWarehouse: Optional[str] = None
    OrderIntervals: Optional[int] = None
    OrderMultiple: Optional[float] = None
    LeadTime: Optional[int] = None
    MinOrderQuantity: Optional[float] = None
    ItemType: Optional[str] = None
    ItemClass: Optional[str] = None
    OutgoingServiceCode: Optional[int] = None
    IncomingServiceCode: Optional[int] = None
    ServiceGroup: Optional[int] = None
    NCMCode: Optional[int] = None
    MaterialType: Optional[str] = None
    MaterialGroup: Optional[int] = None
    ProductSource: Optional[str] = None
    Properties1: Optional[str] = None
    Properties2: Optional[str] = None
    Properties3: Optional[str] = None
    Properties4: Optional[str] = None
    Properties5: Optional[str] = None
    Properties6: Optional[str] = None
    Properties7: Optional[str] = None
    Properties8: Optional[str] = None
    Properties9: Optional[str] = None
    Properties10: Optional[str] = None
    Properties11: Optional[str] = None
    Properties12: Optional[str] = None
    Properties13: Optional[str] = None
    Properties14: Optional[str] = None
    Properties15: Optional[str] = None
    Properties16: Optional[str] = None
    Properties17: Optional[str] = None
    Properties18: Optional[str] = None
    Properties19: Optional[str] = None
    Properties20: Optional[str] = None
    Properties21: Optional[str] = None
    Properties22: Optional[str] = None
    Properties23: Optional[str] = None
    Properties24: Optional[str] = None
    Properties25: Optional[str] = None
    Properties26: Optional[str] = None
    Properties27: Optional[str] = None
    Properties28: Optional[str] = None
    Properties29: Optional[str] = None
    Properties30: Optional[str] = None
    Properties31: Optional[str] = None
    Properties32: Optional[str] = None
    Properties33: Optional[str] = None
    Properties34: Optional[str] = None
    Properties35: Optional[str] = None
    Properties36: Optional[str] = None
    Properties37: Optional[str] = None
    Properties38: Optional[str] = None
    Properties39: Optional[str] = None
    Properties40: Optional[str] = None
    Properties41: Optional[str] = None
    Properties42: Optional[str] = None
    Properties43: Optional[str] = None
    Properties44: Optional[str] = None
    Properties45: Optional[str] = None
    Properties46: Optional[str] = None
    Properties47: Optional[str] = None
    Properties48: Optional[str] = None
    Properties49: Optional[str] = None
    Properties50: Optional[str] = None
    Properties51: Optional[str] = None
    Properties52: Optional[str] = None
    Properties53: Optional[str] = None
    Properties54: Optional[str] = None
    Properties55: Optional[str] = None
    Properties56: Optional[str] = None
    Properties57: Optional[str] = None
    Properties58: Optional[str] = None
    Properties59: Optional[str] = None
    Properties60: Optional[str] = None
    Properties61: Optional[str] = None
    Properties62: Optional[str] = None
    Properties63: Optional[str] = None
    Properties64: Optional[str] = None
    AutoCreateSerialNumbersOnRelease: Optional[str] = None
    DNFEntry: Optional[int] = None
    GTSItemSpec: Optional[str] = None
    GTSItemTaxCategory: Optional[str] = None
    FuelID: Optional[int] = None
    BeverageTableCode: Optional[str] = None
    BeverageGroupCode: Optional[str] = None
    BeverageCommercialBrandCode: Optional[int] = None
    Series: Optional[int] = None
    ToleranceDays: Optional[int] = None
    TypeOfAdvancedRules: Optional[str] = None
    IssuePrimarilyBy: Optional[str] = None
    NoDiscounts: Optional[str] = None
    AssetClass: Optional[str] = None
    AssetGroup: Optional[str] = None 
    InventoryNumber: Optional[str] = None
    Technician: Optional[int] = None
    Employee: Optional[int] = None
    Location: Optional[int] = None
    StatisticalAsset: Optional[str] = None
    Cession: Optional[str] = None
    DeactivateAfterUsefulLife: Optional[str] = None
    ManageByQuantity: Optional[str] = None
    UoMGroupEntry: Optional[int] = None
    InventoryUoMEntry: Optional[int] = None
    DefaultSalesUoMEntry: Optional[int] = None
    DefaultPurchasingUoMEntry: Optional[int] = None
    DepreciationGroup: Optional[str] = None
    AssetSerialNumber: Optional[str] = None
    InventoryWeight: Optional[float] = None
    InventoryWeightUnit: Optional[int] = None
    InventoryWeight1: Optional[float] = None
    InventoryWeightUnit1: Optional[int] = None
    DefaultCountingUnit: Optional[str] = None
    CountingItemsPerUnit: Optional[float] = None
    DefaultCountingUoMEntry: Optional[int] = None
    Excisable: Optional[str] = None
    ChapterID: Optional[int] = None
    NotifyASN: Optional[str] = None
    ProAssNum: Optional[str] = None
    AssVal: Optional[float] = None
    DNFInventory: Optional[int] = None
    DNFIncomingCogs: Optional[int] = None
    DNFOutgoingCogs: Optional[int] = None
    CigTaxCatEntry: Optional[int] = None
    TobTaxCatEntry: Optional[int] = None
    QRCodeSrc: Optional[str] = None
    Lineage: Optional[str] = None
    ItemPrices: Optional[List[dict]] = None
    ItemWarehouseInfoCollection: Optional[List[dict]] = None
    ItemPreferredVendors: Optional[List[dict]] = None
    ItemLocalizationInfos: Optional[List[dict]] = None
    ItemProjects: Optional[List[dict]] = None
    ItemDistributionRules: Optional[List[dict]] = None
    ItemAttributeGroups: Optional[List[dict]] = None
    ItemDepreciationParameters: Optional[List[dict]] = None
    ItemPeriodControls: Optional[List[dict]] = None
    ItemUnitOfMeasurementCollection: Optional[List[dict]] = None
    ItemBarCodeCollection: Optional[List[dict]] = None
    ItemIntrastatExtension: Optional[dict] = None


class ItemSTL(ItemSTLBase):
    pass


class ItemSTLResponse(BaseModel):
    value: List[ItemSTL]


class BusinessPartnerSTLBase(BaseModel):
    CardCode: str
    CardName: str
    CardType: Optional[str] = None
    GroupCode: Optional[int] = None
    Address: Optional[str] = None
    ZipCode: Optional[str] = None
    MailAddress: Optional[str] = None
    MailZipCode: Optional[str] = None
    Phone1: Optional[str] = None
    Phone2: Optional[str] = None
    Fax: Optional[str] = None
    ContactPerson: Optional[str] = None
    Notes: Optional[str] = None
    PayTermsGrpCode: Optional[int] = None
    CreditLimit: Optional[float] = None
    MaxCommitment: Optional[float] = None
    DiscountPercent: Optional[float] = None
    VatStatus: Optional[str] = None
    TaxLiable: Optional[str] = None
    VatGroup: Optional[str] = None
    Currency: Optional[str] = None
    RateDiffAccount: Optional[str] = None
    Cellular: Optional[str] = None
    AvarageLate: Optional[int] = None
    City: Optional[str] = None
    County: Optional[str] = None
    Country: Optional[str] = None
    MailCity: Optional[str] = None
    MailCounty: Optional[str] = None
    MailCountry: Optional[str] = None
    EmailAddress: Optional[str] = None
    Picture: Optional[str] = None
    DefaultAccount: Optional[str] = None
    DefaultBranch: Optional[str] = None
    DefaultBankCode: Optional[str] = None
    AdditionalID: Optional[str] = None
    Pager: Optional[str] = None
    FatherCard: Optional[str] = None
    CardForeignName: Optional[str] = None
    FatherType: Optional[str] = None
    DeductibleAtSource: Optional[str] = None
    DeductionPercent: Optional[float] = None
    DeductionValidUntil: Optional[datetime] = None
    PrimaryContactEmployeeID: Optional[int] = None
    ContactEmployees: Optional[List[dict]] = None
    BPAddresses: Optional[List[dict]] = None
    BPAccountReceivablePaybleCollection: Optional[List[dict]] = None
    BPPaymentMethods: Optional[List[dict]] = None
    BPWithholdingTaxCollection: Optional[List[dict]] = None
    BPPaymentDates: Optional[List[dict]] = None
    BPBranchAssignment: Optional[List[dict]] = None
    BPBankAccounts: Optional[List[dict]] = None
    BPFiscalTaxIDCollection: Optional[List[dict]] = None
    DiscountGroups: Optional[List[dict]] = None
    BPIntrastatExtension: Optional[dict] = None


class BusinessPartnerSTL(BusinessPartnerSTLBase):
    pass


class BusinessPartnerSTLResponse(BaseModel):
    value: List[BusinessPartnerSTL]


class SalesOrderSTLBase(BaseModel):
    DocEntry: Optional[int] = None
    DocNum: Optional[int] = None
    DocType: Optional[str] = None
    HandWritten: Optional[str] = None
    Printed: Optional[str] = None
    DocDate: Optional[datetime] = None
    DocDueDate: Optional[datetime] = None
    CardCode: Optional[str] = None
    CardName: Optional[str] = None
    Address: Optional[str] = None
    NumAtCard: Optional[str] = None
    DocTotal: Optional[float] = None
    AttachmentEntry: Optional[int] = None
    DocCurrency: Optional[str] = None
    DocRate: Optional[float] = None
    Reference1: Optional[str] = None
    Reference2: Optional[str] = None
    Comments: Optional[str] = None
    JournalMemo: Optional[str] = None
    PaymentGroupCode: Optional[int] = None
    DocTime: Optional[str] = None
    SalesPersonCode: Optional[int] = None
    TransportationCode: Optional[int] = None
    Confirmed: Optional[str] = None
    ImportFileNum: Optional[int] = None
    SummeryType: Optional[str] = None
    ContactPersonCode: Optional[int] = None
    ShowSCN: Optional[str] = None
    Series: Optional[int] = None
    TaxDate: Optional[datetime] = None
    PartialSupply: Optional[str] = None
    DocObjectCode: Optional[str] = None
    ShipToCode: Optional[str] = None
    Indicator: Optional[str] = None
    FederalTaxID: Optional[str] = None
    DiscountPercent: Optional[float] = None
    PaymentReference: Optional[str] = None
    CreationDate: Optional[datetime] = None
    UpdateDate: Optional[datetime] = None
    FinancialPeriod: Optional[int] = None
    UserSign: Optional[int] = None
    TransNum: Optional[int] = None
    VatSum: Optional[float] = None
    VatSumSys: Optional[float] = None
    VatSumFc: Optional[float] = None
    NetProcedure: Optional[str] = None
    DocTotalFc: Optional[float] = None
    DocTotalSys: Optional[float] = None
    Form1099: Optional[int] = None
    Box1099: Optional[str] = None
    RevisionPo: Optional[str] = None
    RequriedDate: Optional[datetime] = None
    CancelDate: Optional[datetime] = None
    BlockDunning: Optional[str] = None
    Submitted: Optional[str] = None
    Segment: Optional[int] = None
    PickStatus: Optional[str] = None
    Pick: Optional[str] = None
    PaymentMethod: Optional[str] = None
    PaymentBlock: Optional[str] = None
    PaymentBlockEntry: Optional[int] = None
    CentralBankIndicator: Optional[str] = None
    MaximumCashDiscount: Optional[str] = None
    Reserve: Optional[str] = None
    Project: Optional[str] = None
    ExemptionValidityDateFrom: Optional[datetime] = None
    ExemptionValidityDateTo: Optional[datetime] = None
    WareHouseUpdateType: Optional[str] = None
    Rounding: Optional[str] = None
    ExternalCorrectedDocNum: Optional[str] = None
    InternalCorrectedDocNum: Optional[int] = None
    NextCorrectingDocument: Optional[int] = None
    DeferredTax: Optional[str] = None
    TaxExemptionLetterNum: Optional[str] = None
    WTApplied: Optional[float] = None
    WTAppliedFC: Optional[float] = None
    BillToState: Optional[str] = None
    ShipToState: Optional[str] = None
    NTSApproved: Optional[str] = None
    ETaxWebSite: Optional[int] = None
    ETaxNumber: Optional[str] = None
    NTSApprovedNumber: Optional[str] = None
    EDocGenerationType: Optional[str] = None
    EDocSeries: Optional[int] = None
    EDocNum: Optional[str] = None
    EDocExportFormat: Optional[int] = None
    EDocStatus: Optional[str] = None
    EDocErrorCode: Optional[str] = None
    EDocErrorMessage: Optional[str] = None
    DownPaymentStatus: Optional[str] = None
    GroupSeries: Optional[int] = None
    GroupNumber: Optional[int] = None
    GroupHandWritten: Optional[str] = None
    ReopenOriginalDocument: Optional[str] = None
    ReopenManuallyClosedOrCanceledDocument: Optional[str] = None
    CreateOnlineQuotation: Optional[str] = None
    POSEquipmentNumber: Optional[str] = None
    POSManufacturerSerialNumber: Optional[str] = None
    POSCashierNumber: Optional[int] = None
    ApplyCurrentVATRatesForDownPaymentsToDraw: Optional[str] = None
    ClosingDate: Optional[datetime] = None
    SequenceCode: Optional[int] = None
    SequenceSerial: Optional[int] = None
    SeriesString: Optional[str] = None
    SubSeriesString: Optional[str] = None
    SequenceModel: Optional[str] = None
    UseCorrectionVATGroup: Optional[str] = None
    TotalDiscount: Optional[float] = None
    DownPaymentPercentage: Optional[float] = None
    DownPaymentType: Optional[str] = None
    DownPaymentAmountToDraw: Optional[float] = None
    DownPaymentAmountToDrawFC: Optional[float] = None
    DownPaymentAmountToDrawSC: Optional[float] = None
    DownPaymentsToDraw: Optional[List[dict]] = None
    DocumentLines: Optional[List[dict]] = None
    DocumentAdditionalExpenses: Optional[List[dict]] = None
    WithholdingTaxDataCollection: Optional[List[dict]] = None
    DocumentPackages: Optional[List[dict]] = None
    DocumentSpecialLines: Optional[List[dict]] = None
    DocumentInstallments: Optional[List[dict]] = None
    DownPaymentsToDraw_2: Optional[List[dict]] = None
    TaxExtension: Optional[dict] = None
    AddressExtension: Optional[dict] = None
    SolutionOrder: Optional[dict] = None
    ElectronicProtocols: Optional[List[dict]] = None


class SalesOrderSTL(SalesOrderSTLBase):
    pass


class SalesOrderSTLResponse(BaseModel):
    value: List[SalesOrderSTL]


class DispatchSTLBase(BaseModel):
    U_NumeroDespacho: Optional[str] = None
    U_FechaDespacho: Optional[datetime] = None
    U_CodigoCliente: Optional[str] = None
    U_NombreCliente: Optional[str] = None
    U_DireccionEntrega: Optional[str] = None
    U_CiudadEntrega: Optional[str] = None
    U_TelefonoContacto: Optional[str] = None
    U_PersonaContacto: Optional[str] = None
    U_EstadoDespacho: Optional[str] = None
    U_TransportistaAsignado: Optional[str] = None
    U_VehiculoAsignado: Optional[str] = None
    U_FechaEstimadaEntrega: Optional[datetime] = None
    U_FechaRealEntrega: Optional[datetime] = None
    U_ObservacionesDespacho: Optional[str] = None
    U_ValorTotalDespacho: Optional[float] = None
    U_PesoTotalDespacho: Optional[float] = None
    U_VolumenTotalDespacho: Optional[float] = None
    U_NumeroGuiaTransporte: Optional[str] = None
    U_CostoTransporte: Optional[float] = None
    U_SeguroMercancia: Optional[float] = None
    U_DocumentoReferencia: Optional[str] = None
    U_TipoDespacho: Optional[str] = None
    U_PrioridadDespacho: Optional[str] = None
    U_ZonaEntrega: Optional[str] = None
    U_RutaAsignada: Optional[str] = None
    U_HorarioEntrega: Optional[str] = None
    U_RequiereConfirmacion: Optional[str] = None
    U_FirmaDig: Optional[str] = None
    U_GPS_Latitud: Optional[float] = None
    U_GPS_Longitud: Optional[float] = None
    U_TemperaturaTransporte: Optional[float] = None
    U_HumedadTransporte: Optional[float] = None
    U_CertificadoCalidad: Optional[str] = None
    U_UsuarioCreacion: Optional[str] = None
    U_FechaCreacion: Optional[datetime] = None
    U_UsuarioModificacion: Optional[str] = None
    U_FechaModificacion: Optional[datetime] = None


class DispatchSTL(DispatchSTLBase):
    pass


class DispatchSTLResponse(BaseModel):
    value: List[DispatchSTL]


class InventorySTLBase(BaseModel):
    ItemCode: str
    WhsCode: str
    OnHand: Optional[float] = None
    IsCommited: Optional[float] = None
    OnOrder: Optional[float] = None
    MinStock: Optional[float] = None
    MaxStock: Optional[float] = None
    MinOrder: Optional[float] = None
    Locked: Optional[str] = None
    AvgPrice: Optional[float] = None
    Counted: Optional[float] = None
    WasCountedDate: Optional[datetime] = None
    UserSign: Optional[int] = None
    Frozen: Optional[str] = None
    FrozenFor: Optional[str] = None
    FrozenFrom: Optional[datetime] = None
    FrozenTo: Optional[datetime] = None
    LastPurPrc: Optional[float] = None
    LastPurCur: Optional[str] = None
    LastPurDat: Optional[datetime] = None
    LastEvalPrc: Optional[float] = None
    LastEvalDat: Optional[datetime] = None
    StockValue: Optional[float] = None
    StockValueFc: Optional[float] = None
    StockValueSc: Optional[float] = None
    InvntryAct: Optional[str] = None
    DecreaseAct: Optional[str] = None
    IncreaseAct: Optional[str] = None
    ReturnAct: Optional[str] = None
    ExpensesAct: Optional[str] = None
    EuRevenuesAct: Optional[str] = None
    EuExpensesAct: Optional[str] = None
    FrRevenuesAct: Optional[str] = None
    FrExpensesAct: Optional[str] = None
    ExmptIncome: Optional[str] = None
    PriceDifAct: Optional[str] = None
    VarianceAct: Optional[str] = None
    CostInflation: Optional[str] = None
    DecreasingAct: Optional[str] = None
    IncreasingAct: Optional[str] = None
    ReturningAct: Optional[str] = None
    ExpensOffsettingAct: Optional[str] = None
    WipAccount: Optional[str] = None
    ExchangeRateDifferencesAct: Optional[str] = None
    GoodsClearingAct: Optional[str] = None
    NegativeInventoryAct: Optional[str] = None
    StockInTransitAct: Optional[str] = None
    ShippedGoodsAct: Optional[str] = None
    VatGroup: Optional[str] = None
    FiscalAlreadyPosted: Optional[str] = None
    NonDeductibleTax: Optional[float] = None
    NonDeductibleTaxFC: Optional[float] = None
    NonDeductibleTaxSC: Optional[float] = None
    BaseEntry: Optional[int] = None
    BaseLine: Optional[int] = None
    BaseType: Optional[int] = None
    ReceiptDate: Optional[datetime] = None
    ReceiptTime: Optional[str] = None


class InventorySTL(InventorySTLBase):
    pass


class InventorySTLResponse(BaseModel):
    value: List[InventorySTL]


class TransferSTLBase(BaseModel):    
    DocEntry: Optional[int] = None
    Series: Optional[int] = None
    Printed: Optional[str] = None
    DocDate: Optional[datetime] = None
    DocDueDate: Optional[datetime] = None
    CardCode: Optional[str] = None
    CardName: Optional[str] = None
    Address: Optional[str] = None
    Reference1: Optional[str] = None
    Reference2: Optional[str] = None
    Comments: Optional[str] = None
    JournalMemo: Optional[str] = None
    PriceList: Optional[int] = None
    SalesPersonCode: Optional[int] = None
    FromWarehouse: Optional[str] = None
    ToWarehouse: Optional[str] = None
    CreationDate: Optional[datetime] = None
    UpdateDate: Optional[datetime] = None
    TransNum: Optional[int] = None
    UserSign: Optional[int] = None
    UserSign2: Optional[int] = None
    UseBaseUnits: Optional[str] = None
    TaxDate: Optional[datetime] = None
    Confirmed: Optional[str] = None
    Problem: Optional[str] = None
    Reason: Optional[int] = None
    BPLId: Optional[int] = None
    BPLName: Optional[str] = None
    VATRegNum: Optional[str] = None
    AuthorizedUser: Optional[str] = None
    BranchID: Optional[int] = None
    InstallmentNumber: Optional[int] = None
    PaymentGroupCode: Optional[int] = None
    ExtraMonth: Optional[int] = None
    ExtraDays: Optional[int] = None
    CashDiscountDateOffset: Optional[int] = None
    StartFrom: Optional[str] = None
    NTSApproved: Optional[str] = None
    ETaxWebSite: Optional[int] = None
    ETaxNumber: Optional[str] = None
    NTSApprovedNumber: Optional[str] = None
    EDocGenerationType: Optional[str] = None
    EDocSeries: Optional[int] = None
    EDocNum: Optional[str] = None
    EDocExportFormat: Optional[int] = None
    EDocStatus: Optional[str] = None
    EDocErrorCode: Optional[str] = None
    EDocErrorMessage: Optional[str] = None
    PointOfIssueCode: Optional[str] = None
    Letter: Optional[str] = None
    FolioNumberFrom: Optional[int] = None
    FolioNumberTo: Optional[int] = None
    AttachmentEntry: Optional[int] = None
    DocumentStatus: Optional[str] = None
    ShipToCode: Optional[str] = None
    StockTransferLines: Optional[List[dict]] = None
    StockTransferTaxExtension: Optional[dict] = None
    AddressExtension: Optional[dict] = None


class TransferSTL(TransferSTLBase):
    pass


class TransferSTLResponse(BaseModel):
    value: List[TransferSTL]


class ServiceCallSTLBase(BaseModel):
    ServiceCallID: Optional[int] = None
    Subject: str
    CustomerCode: str
    CustomerName: Optional[str] = None
    ContactCode: Optional[int] = None
    ManufacturerSerialNum: Optional[str] = None
    InternalSerialNum: Optional[str] = None
    ContractID: Optional[int] = None
    ContractEndDate: Optional[datetime] = None
    ResolutionDate: Optional[datetime] = None
    ResolutionTime: Optional[str] = None
    Origin: Optional[int] = None
    ItemCode: Optional[str] = None
    ItemDescription: Optional[str] = None
    ItemGroupCode: Optional[int] = None
    Status: Optional[int] = None
    Priority: Optional[str] = None
    CallType: Optional[int] = None
    ProblemType: Optional[int] = None
    AssigneeCode: Optional[int] = None
    Description: Optional[str] = None
    TechnicianCode: Optional[int] = None
    Resolution: Optional[str] = None
    CreationDate: Optional[datetime] = None
    CreationTime: Optional[str] = None
    Responder: Optional[int] = None
    UpdatedDate: Optional[datetime] = None
    UpdatedTime: Optional[str] = None
    BelongsToAQueue: Optional[str] = None
    ResponseByTime: Optional[str] = None
    ResponseByDate: Optional[datetime] = None
    ResolutionByTime: Optional[str] = None
    ResolutionByDate: Optional[datetime] = None
    ProcessedByDiamond: Optional[str] = None
    CustomerRefNo: Optional[str] = None
    ProblemSubType: Optional[int] = None
    AttachmentEntry: Optional[int] = None
    ServiceBPType: Optional[str] = None
    BusinessPartnerCode: Optional[str] = None
    BusinessPartnerName: Optional[str] = None
    UpdatedBy: Optional[int] = None
    ClosingDate: Optional[datetime] = None
    ClosingTime: Optional[str] = None
    Series: Optional[int] = None
    DocNum: Optional[int] = None
    HandWritten: Optional[str] = None
    PeriodIndicator: Optional[str] = None
    StartDate: Optional[datetime] = None
    StartTime: Optional[str] = None
    EndDate: Optional[datetime] = None
    EndTime: Optional[str] = None
    Duration: Optional[float] = None
    DurationType: Optional[str] = None
    Reminder: Optional[str] = None
    ReminderPeriod: Optional[float] = None
    ReminderType: Optional[str] = None
    Location: Optional[int] = None
    AddressType: Optional[str] = None
    Street: Optional[str] = None
    City: Optional[str] = None
    Room: Optional[str] = None
    State: Optional[str] = None
    Country: Optional[str] = None
    District: Optional[str] = None
    ZipCode: Optional[str] = None
    Block: Optional[str] = None
    County: Optional[str] = None
    ShowInCalendar: Optional[str] = None
    CustomizedFields: Optional[List[dict]] = None
    ActivityLocation: Optional[int] = None
    ServiceCallActivities: Optional[List[dict]] = None
    ServiceCallInventoryExpenses: Optional[List[dict]] = None
    ServiceCallSolutions: Optional[List[dict]] = None
    ServiceCallSchedulings: Optional[List[dict]] = None
    ServiceCallBPAddressComponents: Optional[List[dict]] = None


class ServiceCallSTL(ServiceCallSTLBase):
    pass


class ServiceCallSTLResponse(BaseModel):
    value: List[ServiceCallSTL]


class InvoiceSTLBase(BaseModel):
    DocEntry: Optional[int] = None
    DocNum: Optional[int] = None
    DocType: Optional[str] = None
    HandWritten: Optional[str] = None
    Printed: Optional[str] = None
    DocDate: Optional[datetime] = None
    DocDueDate: Optional[datetime] = None
    CardCode: Optional[str] = None
    CardName: Optional[str] = None
    Address: Optional[str] = None
    NumAtCard: Optional[str] = None
    DocTotal: Optional[float] = None
    AttachmentEntry: Optional[int] = None
    DocCurrency: Optional[str] = None
    DocRate: Optional[float] = None
    Reference1: Optional[str] = None
    Reference2: Optional[str] = None
    Comments: Optional[str] = None
    JournalMemo: Optional[str] = None
    PaymentGroupCode: Optional[int] = None
    DocTime: Optional[str] = None
    SalesPersonCode: Optional[int] = None
    TransportationCode: Optional[int] = None
    Confirmed: Optional[str] = None
    ImportFileNum: Optional[int] = None
    SummeryType: Optional[str] = None
    ContactPersonCode: Optional[int] = None
    ShowSCN: Optional[str] = None
    Series: Optional[int] = None
    TaxDate: Optional[datetime] = None
    PartialSupply: Optional[str] = None
    DocObjectCode: Optional[str] = None
    ShipToCode: Optional[str] = None
    Indicator: Optional[str] = None
    FederalTaxID: Optional[str] = None
    DiscountPercent: Optional[float] = None
    PaymentReference: Optional[str] = None
    CreationDate: Optional[datetime] = None
    UpdateDate: Optional[datetime] = None
    FinancialPeriod: Optional[int] = None
    TransNum: Optional[int] = None
    VatSum: Optional[float] = None
    VatSumSys: Optional[float] = None
    VatSumFc: Optional[float] = None
    NetProcedure: Optional[str] = None
    DocTotalFc: Optional[float] = None
    DocTotalSys: Optional[float] = None
    Form1099: Optional[int] = None
    Box1099: Optional[str] = None
    RevisionPo: Optional[str] = None
    RequriedDate: Optional[datetime] = None
    CancelDate: Optional[datetime] = None
    BlockDunning: Optional[str] = None
    Submitted: Optional[str] = None
    Segment: Optional[int] = None
    PickStatus: Optional[str] = None
    Pick: Optional[str] = None
    PaymentMethod: Optional[str] = None
    PaymentBlock: Optional[str] = None
    PaymentBlockEntry: Optional[int] = None
    CentralBankIndicator: Optional[str] = None
    MaximumCashDiscount: Optional[str] = None
    Reserve: Optional[str] = None
    Project: Optional[str] = None
    ExemptionValidityDateFrom: Optional[datetime] = None
    ExemptionValidityDateTo: Optional[datetime] = None
    WareHouseUpdateType: Optional[str] = None
    Rounding: Optional[str] = None
    ExternalCorrectedDocNum: Optional[str] = None
    InternalCorrectedDocNum: Optional[int] = None
    NextCorrectingDocument: Optional[int] = None
    DeferredTax: Optional[str] = None
    TaxExemptionLetterNum: Optional[str] = None
    WTApplied: Optional[float] = None
    WTAppliedFC: Optional[float] = None
    BillToState: Optional[str] = None
    ShipToState: Optional[str] = None
    NTSApproved: Optional[str] = None
    ETaxWebSite: Optional[int] = None
    ETaxNumber: Optional[str] = None
    NTSApprovedNumber: Optional[str] = None
    EDocGenerationType: Optional[str] = None
    EDocSeries: Optional[int] = None
    EDocNum: Optional[str] = None
    EDocExportFormat: Optional[int] = None
    EDocStatus: Optional[str] = None
    EDocErrorCode: Optional[str] = None
    EDocErrorMessage: Optional[str] = None
    DownPaymentStatus: Optional[str] = None
    GroupSeries: Optional[int] = None
    GroupNumber: Optional[int] = None
    GroupHandWritten: Optional[str] = None
    ReopenOriginalDocument: Optional[str] = None
    ReopenManuallyClosedOrCanceledDocument: Optional[str] = None
    CreateOnlineQuotation: Optional[str] = None
    POSEquipmentNumber: Optional[str] = None
    POSManufacturerSerialNumber: Optional[str] = None
    POSCashierNumber: Optional[int] = None
    ApplyCurrentVATRatesForDownPaymentsToDraw: Optional[str] = None
    ClosingDate: Optional[datetime] = None
    SequenceCode: Optional[int] = None
    SequenceSerial: Optional[int] = None
    SeriesString: Optional[str] = None
    SubSeriesString: Optional[str] = None
    SequenceModel: Optional[str] = None
    UseCorrectionVATGroup: Optional[str] = None
    TotalDiscount: Optional[float] = None
    DownPaymentPercentage: Optional[float] = None
    DownPaymentType: Optional[str] = None
    DownPaymentAmountToDraw: Optional[float] = None
    DownPaymentAmountToDrawFC: Optional[float] = None
    DownPaymentAmountToDrawSC: Optional[float] = None
    DocumentLines: Optional[List[dict]] = None
    DocumentAdditionalExpenses: Optional[List[dict]] = None
    WithholdingTaxDataCollection: Optional[List[dict]] = None
    DocumentPackages: Optional[List[dict]] = None
    DocumentSpecialLines: Optional[List[dict]] = None
    DocumentInstallments: Optional[List[dict]] = None
    DownPaymentsToDraw: Optional[List[dict]] = None
    TaxExtension: Optional[dict] = None
    AddressExtension: Optional[dict] = None
    DocumentReferences: Optional[List[dict]] = None
    ElectronicProtocols: Optional[List[dict]] = None


class InvoiceSTL(InvoiceSTLBase):
    pass


class InvoiceSTLResponse(BaseModel):
    value: List[InvoiceSTL]