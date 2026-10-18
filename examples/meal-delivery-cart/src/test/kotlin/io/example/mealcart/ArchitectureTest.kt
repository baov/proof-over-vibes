package io.example.mealcart

import com.tngtech.archunit.base.DescribedPredicate
import com.tngtech.archunit.core.domain.JavaCall
import com.tngtech.archunit.core.domain.JavaClass
import com.tngtech.archunit.core.domain.SourceCodeLocation
import com.tngtech.archunit.core.domain.JavaClass.Predicates.resideInAnyPackage
import com.tngtech.archunit.core.domain.JavaClass.Predicates.resideOutsideOfPackages
import com.tngtech.archunit.core.importer.ClassFileImporter
import com.tngtech.archunit.core.importer.ImportOption
import com.tngtech.archunit.junit.AnalyzeClasses
import com.tngtech.archunit.junit.ArchTest
import com.tngtech.archunit.lang.ArchCondition
import com.tngtech.archunit.lang.ArchRule
import com.tngtech.archunit.lang.ConditionEvents
import com.tngtech.archunit.lang.SimpleConditionEvent
import com.tngtech.archunit.lang.syntax.ArchRuleDefinition.classes
import com.tngtech.archunit.lang.syntax.ArchRuleDefinition.fields
import com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noClasses
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

/**
 * INV-001 to INV-004, from ADR-0001 and ADR-0002; INV-007, from ADR-0004. Technical test: it has no test-case (see INV-005 exclusions).
 * Severity: warn (see docs/technical/invariants.md). Run it with: python3 tools/harness/check_layers.py
 *
 * The base package is named here and in pom.xml (`base.package`): change both together. On an empty codebase the
 * rules pass vacuously, and a wrong package name would keep them passing.
 */
@AnalyzeClasses(packages = ["io.example.mealcart"], importOptions = [ImportOption.DoNotIncludeTests::class])
class ArchitectureTest {

    companion object {
        private const val BASE = "io.example.mealcart"
        private const val DOMAIN = "$BASE.domain.."
        private const val APPLICATION = "$BASE.application.."
        private const val MONEY = "$BASE.domain.money.."

        // What the standard library of Kotlin on the JVM brings into every class's bytecode.
        // `org.jetbrains.annotations` holds the @NotNull/@Nullable that the Kotlin compiler writes on its own.
        private val STDLIB = arrayOf("java..", "kotlin..", "org.jetbrains.annotations..")

        private const val FIX_LAYERS =
            " -- move the dependency behind a port owned by `application` and implemented in an adapter " +
                "(see INV-001 in docs/technical/invariants.md and ADR-0001)"
        private const val FIX_ROUNDING =
            " -- call the single rounding function of `domain.money` instead (see INV-002 and ADR-0001)"
        private const val FIX_FLOAT =
            " -- hold amounts as `Money` (Long minor units) and rates as `Percentage` (integer over a power of ten) " +
                "(see INV-003 and ADR-0002)"
        private const val FIX_PURE =
            " -- the core takes everything as arguments; if it needs the clock, randomness or I/O, " +
                "that is a port owned by `application` (see INV-004)"

        private const val FIX_FINAL =
            " -- make the field a `val`; hold no cache, memo or counter in the core, and compute from the arguments " +
                "(see INV-007 and ADR-0004)"

        private fun fieldsAreFinal(inside: DescribedPredicate<JavaClass>): ArchRule = fields()
            .that().areDeclaredInClassesThat(inside)
            .should().beFinal()
            .allowEmptyShould(true)
            .`as`("[INV-007] every field of `domain` and `application` is final$FIX_FINAL")

        private fun isCallTo(owners: DescribedPredicate<JavaClass>, names: Set<String>): DescribedPredicate<JavaCall<*>> =
            object : DescribedPredicate<JavaCall<*>>("calls ${names.joinToString()}") {
                override fun test(call: JavaCall<*>): Boolean =
                    owners.test(call.targetOwner) && call.name in names
            }

        private val ROUNDING_NAMES = setOf(
            "round", "rint", "floor", "ceil", "truncate", "roundToInt", "roundToLong",
            "floorDiv", "ceilDiv", "setScale",
        )
        private val ROUNDING_OWNERS = DescribedPredicate.describe<JavaClass>("a rounding API") {
            it.fullName in setOf("java.lang.Math", "java.lang.StrictMath", "java.math.BigDecimal") ||
                it.packageName == "kotlin.math" || it.packageName.startsWith("kotlin.math.")
        }

        private val FLOATING = setOf("double", "float", "java.lang.Double", "java.lang.Float", "java.math.BigDecimal")

        private fun noFloatingPoint(): ArchCondition<JavaClass> =
            object : ArchCondition<JavaClass>("not use double, float or BigDecimal") {
                override fun check(item: JavaClass, events: ConditionEvents) {
                    fun report(what: String, type: String, location: SourceCodeLocation) {
                        events.add(SimpleConditionEvent.violated(item, "$what uses $type $location"))
                    }
                    item.fields.filter { it.rawType.fullName in FLOATING }
                        .forEach { report("field ${item.simpleName}.${it.name}", it.rawType.simpleName, it.sourceCodeLocation) }
                    item.codeUnits.forEach { unit ->
                        (listOf(unit.rawReturnType) + unit.rawParameterTypes)
                            .filter { it.fullName in FLOATING }
                            .forEach { report("${item.simpleName}.${unit.name}", it.simpleName, unit.sourceCodeLocation) }
                        unit.callsFromSelf
                            .filter { it.targetOwner.fullName in FLOATING || it.target.rawReturnType.fullName in FLOATING }
                            .forEach { report("${item.simpleName}.${unit.name}", it.targetOwner.simpleName, it.sourceCodeLocation) }
                    }
                }
            }

        @JvmField
        @ArchTest
        val domainDependsOnTheStdlibOnly: ArchRule = noClasses()
            .that().resideInAPackage(DOMAIN)
            .should().dependOnClassesThat(
                resideOutsideOfPackages(*STDLIB, DOMAIN)
            )
            .allowEmptyShould(true)
            .`as`("[INV-001] `domain` imports nothing but the Kotlin and JDK standard library and itself$FIX_LAYERS")

        @JvmField
        @ArchTest
        val applicationDependsOnDomainOnly: ArchRule = noClasses()
            .that().resideInAPackage(APPLICATION)
            .should().dependOnClassesThat(
                resideOutsideOfPackages(*STDLIB, DOMAIN, APPLICATION)
            )
            .allowEmptyShould(true)
            .`as`("[INV-001] `application` depends on `domain` and the standard library only$FIX_LAYERS")

        @JvmField
        @ArchTest
        val nothingInnerImportsAdapters: ArchRule = noClasses()
            .that().resideInAnyPackage(DOMAIN, APPLICATION)
            .should().dependOnClassesThat().resideInAPackage("$BASE.adapters..")
            .allowEmptyShould(true)
            .`as`("[INV-001] nothing in `domain` or `application` imports `adapters`$FIX_LAYERS")

        @JvmField
        @ArchTest
        val roundingHappensInDomainMoneyOnly: ArchRule = noClasses()
            .that().resideOutsideOfPackage(MONEY)
            .should().callMethodWhere(isCallTo(ROUNDING_OWNERS, ROUNDING_NAMES))
            .orShould().dependOnClassesThat().haveFullyQualifiedName("java.math.RoundingMode")
            .allowEmptyShould(true)
            .`as`("[INV-002] only `domain.money` rounds (no Math.round/floor/ceil, kotlin.math rounding, setScale, RoundingMode elsewhere)$FIX_ROUNDING")

        @JvmField
        @ArchTest
        val noFloatingPointForMoney: ArchRule = classes()
            .that().resideInAnyPackage(DOMAIN, APPLICATION)
            .should(noFloatingPoint())
            .allowEmptyShould(true)
            .`as`("[INV-003] `domain` and `application` use no Double, Float or BigDecimal$FIX_FLOAT")

        @JvmField
        @ArchTest
        val coreIsPure: ArchRule = noClasses()
            .that().resideInAnyPackage(DOMAIN, APPLICATION)
            .should().dependOnClassesThat(
                resideInAnyPackage(
                    "java.time..", "java.io..", "java.nio..", "java.net..", "java.sql..", "java.util.concurrent..",
                    "kotlin.random..", "kotlin.io..", "kotlin.concurrent..", "kotlin.time..",
                ).or(DescribedPredicate.describe("a source of randomness, environment or time") {
                    it.fullName in setOf("java.util.Random", "java.util.Date", "java.util.Calendar", "java.lang.System", "java.lang.Thread", "java.lang.Runtime")
                })
            )
            .allowEmptyShould(true)
            .`as`("[INV-004] `domain` and `application` read no clock, randomness, environment, file or network$FIX_PURE")

        @JvmField
        @ArchTest
        val coreFieldsAreFinal: ArchRule = fieldsAreFinal(resideInAnyPackage(DOMAIN, APPLICATION))
    }

    // Self-test of INV-007 on throwaway fixtures (never on feature code): the rule must flag a mutable field
    // and let a `val`, a `const`, an `object` and a companion pass.
    class FixtureGood(val a: Int) {
        val b: List<Int> = listOf(a)
        companion object { const val C = 1; val D = "d" }
    }

    object FixtureObject { val e = 1 }

    class FixtureBadVar { var counter = 0 }

    class FixtureBadLateinit { lateinit var cache: String }

    object FixtureBadObject { var memo = mutableMapOf<Int, Int>() }

    private fun violationsOnFixtures(): List<String> {
        val classes = ClassFileImporter().importClasses(
            FixtureGood::class.java, FixtureGood.Companion::class.java, FixtureObject::class.java,
            FixtureBadVar::class.java, FixtureBadLateinit::class.java, FixtureBadObject::class.java,
        )
        val inside = DescribedPredicate.describe<JavaClass>("a fixture") { it.simpleName.startsWith("Fixture") }
        val result = fieldsAreFinal(inside).evaluate(classes)
        return result.failureReport.details.map { it.toString() }
    }

    @Test
    fun `INV-007 flags var, lateinit and a mutable object field`() {
        val details = violationsOnFixtures().joinToString("\n")
        assertTrue("FixtureBadVar.counter" in details, details)
        assertTrue("FixtureBadLateinit.cache" in details, details)
        assertTrue("FixtureBadObject.memo" in details, details)
    }

    @Test
    fun `INV-007 lets val, const, object and companion fields pass`() {
        val details = violationsOnFixtures().joinToString("\n")
        assertTrue("FixtureGood" !in details, details)
        assertTrue("FixtureObject" !in details, details)
        assertEquals(3, violationsOnFixtures().size, details)
    }
}
