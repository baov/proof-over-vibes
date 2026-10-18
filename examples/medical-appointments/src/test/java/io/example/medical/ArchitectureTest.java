package io.example.medical;

import com.tngtech.archunit.core.importer.ImportOption;
import com.tngtech.archunit.junit.AnalyzeClasses;
import com.tngtech.archunit.junit.ArchTest;
import com.tngtech.archunit.lang.ArchRule;

import static com.tngtech.archunit.core.domain.JavaClass.Predicates.resideInAPackage;
import static com.tngtech.archunit.core.domain.JavaClass.Predicates.resideOutsideOfPackage;
import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noClasses;
import static com.tngtech.archunit.base.DescribedPredicate.not;

/**
 * INV-001, ADR-0001: dependency rule of the hexagonal architecture.
 * Technical test: it has no test-case (see INV-002 exclusions). Severity: warn (see docs/technical/invariants.md).
 * Run it with: bash tools/harness/check_layers.sh
 */
@AnalyzeClasses(packages = "io.example.medical", importOptions = ImportOption.DoNotIncludeTests.class)
class ArchitectureTest {

    private static final String FIX =
            " -- move the dependency behind a port owned by `application`, implemented in `adapters` "
            + "(see INV-001 in docs/technical/invariants.md and ADR-0001)";

    @ArchTest
    static final ArchRule domainDependsOnTheJdkOnly = noClasses()
            .that().resideInAPackage("..domain..")
            .should().dependOnClassesThat(
                    resideOutsideOfPackage("java..")
                            .and(not(resideInAPackage("..domain.."))))
            .allowEmptyShould(true)
            .as("[INV-001] `domain` imports nothing but java.* and itself" + FIX);

    @ArchTest
    static final ArchRule applicationDependsOnDomainOnly = noClasses()
            .that().resideInAPackage("..application..")
            .should().dependOnClassesThat(
                    resideOutsideOfPackage("java..")
                            .and(not(resideInAPackage("..domain..")))
                            .and(not(resideInAPackage("..application.."))))
            .allowEmptyShould(true)
            .as("[INV-001] `application` depends on `domain` and the JDK only" + FIX);

    @ArchTest
    static final ArchRule nothingInnerImportsAdapters = noClasses()
            .that().resideInAnyPackage("..domain..", "..application..")
            .should().dependOnClassesThat().resideInAPackage("..adapters..")
            .allowEmptyShould(true)
            .as("[INV-001] nothing in `domain` or `application` imports `adapters`" + FIX);
}
