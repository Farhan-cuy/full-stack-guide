# Backend: Java/Kotlin (Spring) and .NET (ASP.NET Core)

Orientation for two enterprise stacks that share concepts (dependency injection, layered services, ORM, declarative security).

## Detection
- Spring: `pom.xml` or `build.gradle(.kts)` with Spring Boot; `@SpringBootApplication`; controllers annotated `@RestController`; JPA/Hibernate, jOOQ, or MyBatis; Flyway or Liquibase migrations.
- .NET: `*.csproj` / `*.sln`, `Program.cs` (minimal hosting) or `Startup.cs`; controllers or minimal API endpoints; EF Core or Dapper; EF migrations.
- Tests: JUnit/Mockito/Testcontainers, or xUnit/NUnit/MSTest with `WebApplicationFactory`.

## Idioms
- Spring: controller → service → repository; Bean Validation (`@Valid`) at the boundary; method or URL security (`@PreAuthorize`, security filter chain); `@Transactional` at the service boundary; global error handling (`@ControllerAdvice` or `ProblemDetail`); DTOs separate from entities.
- .NET: model validation or FluentValidation; policy-based authorization (`[Authorize(Policy = ...)]`) with resource checks in the handler; a scoped `DbContext`; transactions through `SaveChanges` or explicit transactions; `ProblemDetails` for errors; concurrency tokens (`rowversion`) for optimistic locking.
- Test web behavior through the real pipeline (MockMvc / `WebApplicationFactory`), including the security filters.

## Pitfalls
- Spring: `@Transactional` ignored on self-invocation or non-public methods; rollback rules for checked exceptions; lazy-loaded entities serialized directly; open-session-in-view hiding N+1.
- .NET: tracking queries by default and N+1 without `Include`; forgetting `AsNoTracking` for read-only queries; async methods called synchronously; `DateTime` kind confusion.
- Exposing entities instead of DTOs; leaking internal fields or relationships.
- Authorization attributes on controllers but missing object-level checks inside handlers.
- Nullability annotations or nullable reference types ignored.

## Verify
- Spring: `./mvnw test` or `mvn test`, `./gradlew test`, `./gradlew build`; configured static analysis
- .NET: `dotnet build`, `dotnet test`, and `dotnet format --verify-no-changes` if used
- Run migrations on a scratch database and tests with a real database engine where behavior depends on it

## Version-sensitive
Check installed versions: Spring Boot 2 vs 3 (Java 17+, `jakarta.*` namespace), Spring Security configuration style, Hibernate major version, .NET target framework and hosting model, EF Core major version, Java/C# language version.
