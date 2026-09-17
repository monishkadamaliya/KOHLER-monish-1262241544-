from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session

from app.catalogue.repository import count_products, count_relationships, get_components, get_product, get_relationships, list_products
from app.colour.schemas import PaletteRequest, PaletteResponse
from app.colour.service import ColourIntelligenceService
from app.constraints.schemas import ConstraintRequest, ConstraintResponse
from app.constraints.service import validate_candidates
from app.constraints.spatial import validate_spatial
from app.constraints.spatial_schemas import SpatialValidationRequest, SpatialValidationResponse
from app.db.database import engine, get_db
from app.db.models import Base
from app.db.schemas import ProductOut, RelationshipOut
from app.intelligence.schemas import IntentParseRequest, IntentParseResponse
from app.intelligence.service import IntentService
from app.optimization.configuration_schemas import ConfigurationSearchRequest, ConfigurationSearchResponse
from app.optimization.configuration_solver import FeasibleConfigurationSolver
from app.optimization.schemas import OptimizationRequest, OptimizationResponse
from app.optimization.service import BathroomOptimizer
from app.orchestration.schemas import DesignGenerateRequest, DesignGenerateResponse
from app.orchestration.service import DesignOrchestrator
from app.retrieval.schemas import RetrievalRequest, RetrievalResponse
from app.retrieval.service import CatalogueRetrievalService

app = FastAPI(
    title="KOHLER AI Bathroom Intelligence API",
    version="1.0.0",
    description="Catalogue truth + retrieval + deterministic constraints/spatial validation + optimization + guarded Nova intent extraction + catalogue-grounded colour intelligence + end-to-end design orchestration.",
)


@app.on_event("startup")
def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "engine": "catalogue"}


@app.get("/catalogue/stats")
def catalogue_stats(db: Session = Depends(get_db)) -> dict[str, int]:
    return {"products": count_products(db), "relationships": count_relationships(db)}


@app.get("/products/{sku}", response_model=ProductOut)
def product(sku: str, db: Session = Depends(get_db)) -> ProductOut:
    item = get_product(db, sku)
    if item is None:
        raise HTTPException(status_code=404, detail=f"SKU not found: {sku}")
    return item


@app.get("/products", response_model=list[ProductOut])
def products(category: str | None = None, domain: str | None = None, max_price: float | None = Query(default=None, ge=0), min_price: float | None = Query(default=None, ge=0), finish: str | None = None, search: str | None = None, limit: int = Query(default=100, ge=1, le=500), db: Session = Depends(get_db)) -> list[ProductOut]:
    return list_products(db, category, domain, max_price, min_price, finish, search, limit)


@app.get("/products/{sku}/relationships", response_model=list[RelationshipOut])
def relationships(sku: str, db: Session = Depends(get_db)) -> list[RelationshipOut]:
    return get_relationships(db, sku)


@app.get("/products/{sku}/components", response_model=list[RelationshipOut])
def components(sku: str, db: Session = Depends(get_db)) -> list[RelationshipOut]:
    return get_components(db, sku)


@app.post("/retrieval/search", response_model=RetrievalResponse)
def retrieval_search(request: RetrievalRequest, db: Session = Depends(get_db)) -> RetrievalResponse:
    return CatalogueRetrievalService(db).search(request)


@app.post("/constraints/validate", response_model=ConstraintResponse)
def constraints_validate(request: ConstraintRequest, db: Session = Depends(get_db)) -> ConstraintResponse:
    return validate_candidates(db, request)


@app.post("/constraints/spatial", response_model=SpatialValidationResponse)
def constraints_spatial(request: SpatialValidationRequest, db: Session = Depends(get_db)) -> SpatialValidationResponse:
    return validate_spatial(db, request)


@app.post("/optimize", response_model=OptimizationResponse)
def optimize(request: OptimizationRequest, db: Session = Depends(get_db)) -> OptimizationResponse:
    return BathroomOptimizer(db).optimize(request)


@app.post("/optimize/configuration", response_model=ConfigurationSearchResponse)
def optimize_configuration(request: ConfigurationSearchRequest, db: Session = Depends(get_db)) -> ConfigurationSearchResponse:
    if request.optimization.room_width_mm is None or request.optimization.room_depth_mm is None:
        raise HTTPException(status_code=422, detail="room_width_mm and room_depth_mm are required for feasible configuration placement.")
    return FeasibleConfigurationSolver(db).search(request)


@app.post("/intelligence/parse-intent", response_model=IntentParseResponse)
def parse_intent(request: IntentParseRequest) -> IntentParseResponse:
    return IntentService().parse(request)


@app.post("/colour/palette", response_model=PaletteResponse)
def colour_palette(request: PaletteRequest, db: Session = Depends(get_db)) -> PaletteResponse:
    return ColourIntelligenceService(db).generate(request)


@app.post("/design/generate", response_model=DesignGenerateResponse)
def generate_design(request: DesignGenerateRequest, db: Session = Depends(get_db)) -> DesignGenerateResponse:
    return DesignOrchestrator(db).generate(request)
